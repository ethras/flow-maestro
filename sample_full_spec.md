# Expense Management Feature - Final Specification v3.0

**Client:** C Informatique
**Date:** 2025-11-06
**Status:** Ready for Implementation

---

## Overview

Simple expense management system where employees submit individual expenses with receipt attachments. Managers approve/reject, and administrators create bulk payments. Features AI receipt extraction, multi-currency support via Frankfurter API, and frontend PDF export.

---

## Core Features

### 1. Individual Expense Submission
- Employees create expenses **one by one** (no parent grouping)
- Each expense has: date, category, description, amount, currency, receipt
- Mobile-first: capture receipt with camera, AI extracts data
- Web: upload receipt, AI extraction with manual review

### 2. Expense Categories
- **Meal** (Frais de repas)
- **Parking** (Frais de parking)
- **Vehicle** (Frais voiture)
- **Fuel** (Frais carburant)
- **Subscription** (Abonnement)
- **ClientPurchase** (Achat client)

### 3. Status Workflow
```
Draft → Approved (automatic on submit) → Paid
  ↓
Rejected (by manager with reason)
```

### 4. Multi-Currency with Frankfurter API
- Enter amount in any currency (CHF, EUR, USD, etc.)
- Automatic conversion to CHF using **Frankfurter API**
  - Free, no API key, no limits
  - European Central Bank data
  - `https://api.frankfurter.app`
- Conversion happens at expense creation time
- Store: original amount + currency, CHF amount, exchange rate value

### 5. AI Receipt Extraction
- **Azure Document Intelligence** (prebuilt receipt model)
- Extracts: date, amount, currency, merchant name
- User reviews and confirms/edits before saving
- Manual fallback if AI fails

### 6. Payment Processing
- Admins create bulk payments
- One payment includes multiple expenses
- Three grouping methods:
  - By date range
  - By category
  - Manual selection
- Expenses marked as "Paid" when included in payment

### 7. PDF Export (Frontend)
- Generate expense reports as PDF in browser
- Using **pdfmake** (same as invoices)
- Same filtering as payments (date, category, selection)
- Display in modal viewer, option to download

---

## Data Model

### Expense Entity

```typescript
type Expense extending Timestamp {
  // Identity
  required link employee -> Employee { on target delete delete source; }

  // Expense Details
  required property expenseDate -> cal::local_date;
  required property category -> ExpenseCategory;
  required property description -> str;  // Merchant name
  property notes -> str;

  // Financial - Original Currency
  required property amount -> decimal;
  required property currency -> Currency { default := Currency.CHF; }

  // Financial - CHF Conversion
  required property amountCHF -> decimal;
  property exchangeRate -> decimal;  // Rate value used (for audit)
  property exchangeRateDate -> cal::local_date;  // Date of conversion

  // Receipt
  property receiptBlobName -> str;
  property receiptFileName -> str;
  property receiptMimeType -> str;
  property receiptPageCount -> int16;  // For PDFs

  // AI Metadata
  property extractedByAI -> bool { default := false; }
  property aiConfidenceScore -> decimal;  // 0.0 to 1.0
  property aiRawResponse -> json;

  // Workflow
  required property status -> ExpenseStatus { default := ExpenseStatus.Draft; }
  property submittedAt -> datetime;
  link rejectedBy -> Employee { on target delete allow; }
  property rejectedAt -> datetime;
  property rejectionReason -> str;

  // Payment
  link payment -> ExpensePayment { on target delete allow; }
  property paidAt -> datetime;

  // Constraints & Indexes
  constraint exclusive on (.receiptBlobName);
  index on (.expenseDate);
  index on (.category);
  index on (.status);
  index on (.employee);
}
```

### ExpensePayment Entity

```typescript
type ExpensePayment extending Timestamp {
  // Payment Details
  required property paymentDate -> cal::local_date;
  required property totalAmount -> decimal;
  property notes -> str;

  // Creator
  required link createdBy -> Employee { on target delete allow; }

  // Backlinks
  multi link expenses := .<payment[is Expense];

  // Computed
  property expenseCount := count(.expenses);
  property totalCalculated := sum(.expenses.amountCHF);

  // Trigger: Mark expenses as paid
  trigger markExpensesPaid
    after insert
    for each do (
      update .expenses
      set {
        status := ExpenseStatus.Paid,
        paidAt := datetime_of_statement()
      }
    );
}
```

### Enums

```typescript
scalar type ExpenseStatus extending enum<Draft, Approved, Rejected, Paid>;

scalar type ExpenseCategory extending enum<
  Meal, Parking, Vehicle, Fuel, Subscription, ClientPurchase
>;

scalar type Currency extending enum<
  CHF, EUR, USD, GBP, JPY, CAD, AUD, NZD, SEK, NOK, DKK,
  CZK, PLN, HUF, BGN, RON, TRY, ISK, HRK, RUB, BRL,
  CNY, INR, IDR, ILS, KRW, MXN, MYR, PHP, SGD, THB, ZAR
>;
```

### Permissions

```typescript
scalar type Permissions extending enum<
  // ... existing ...

  // Expenses
  ExpensesView,
  ExpensesInsert,
  ExpensesUpdate,
  ExpensesDelete,
  ExpensesApprove,    // Managers
  ExpensesReject,     // Managers

  // Payments
  ExpensePaymentsView,
  ExpensePaymentsCreate,
  ExpensePaymentsDelete,
>;
```

---

## API Architecture

### Backend Module Structure

```
apps/edgedb-api/cinformatique/src/app/expenses/
├── expenses.module.ts
├── expense.service.ts
├── expense.repository.ts
├── expense.resolver.ts
├── expense.shapes.ts
├── interfaces/
│   ├── expense.interface.ts
│   └── expense-query.interface.ts
├── dto/
│   ├── expense.object.ts
│   ├── create-expense.input.ts
│   ├── create-expense-with-receipt.input.ts
│   ├── update-expense.input.ts
│   └── expense-query.input.ts
├── payments/
│   ├── expense-payment.service.ts
│   ├── expense-payment.repository.ts
│   ├── expense-payment.resolver.ts
│   └── dto/
│       ├── expense-payment.object.ts
│       └── create-expense-payment.input.ts
└── services/
    ├── currency-conversion.service.ts  # Frankfurter API
    └── receipt-extraction.service.ts   # Azure Document Intelligence
```

### Currency Conversion Service (Simplified)

```typescript
@Injectable()
export class CurrencyConversionService {
  private readonly frankfurterUrl = 'https://api.frankfurter.app';

  async convertToCHF(
    amount: Decimal,
    fromCurrency: Currency,
    date?: LocalDate,
  ): Promise<{
    amountCHF: Decimal;
    exchangeRate: Decimal;
    exchangeRateDate: LocalDate;
  }> {
    // If already CHF, no conversion
    if (fromCurrency === Currency.CHF) {
      return {
        amountCHF: amount,
        exchangeRate: new Decimal(1),
        exchangeRateDate: LocalDate.from(new Date()),
      };
    }

    // Fetch rate from Frankfurter
    const rateDate = date || LocalDate.from(new Date());
    const dateStr = rateDate.toString(); // YYYY-MM-DD

    // Get rate: EUR to fromCurrency and EUR to CHF
    const url = `${this.frankfurterUrl}/${dateStr}?to=${fromCurrency},CHF`;
    const response = await fetch(url);
    const data = await response.json();

    // Convert: fromCurrency → EUR → CHF
    const fromRate = new Decimal(data.rates[fromCurrency]);
    const chfRate = new Decimal(data.rates.CHF);

    // amountInEUR = amount / fromRate
    // amountInCHF = amountInEUR * chfRate
    const amountCHF = amount.div(fromRate).times(chfRate);

    return {
      amountCHF,
      exchangeRate: chfRate.div(fromRate), // Direct fromCurrency→CHF rate
      exchangeRateDate: rateDate,
    };
  }
}
```

### GraphQL API

#### Queries

```graphql
type Query {
  # Expenses
  expense(id: String!): Expense
  expenses(
    where: ExpenseWhereInput
    orderBy: [OrderByInput!]
    skip: Int
    take: Int
  ): ExpenseQueryResult!

  # Payments
  expensePayment(id: String!): ExpensePayment
  expensePayments(...): ExpensePaymentQueryResult!

  # Utilities
  exchangeRate(from: Currency!, to: Currency!, date: LocalDate): Float!
}
```

#### Mutations

```graphql
type Mutation {
  # Expense CRUD
  createExpense(input: CreateExpenseInput!): Expense!
  createExpenseWithReceipt(input: CreateExpenseWithReceiptInput!): ExpenseWithUploadUrl!
  updateExpense(input: UpdateExpenseInput!): Expense!
  deleteExpense(id: String!): IdObject!

  # Workflow
  submitExpense(id: String!): Expense!
  approveExpense(id: String!): Expense!
  rejectExpense(id: String!, reason: String!): Expense!

  # AI Extraction
  extractReceiptData(expenseId: String!): ExtractedReceiptData!
  applyExtractedData(expenseId: String!, data: ApplyExtractedDataInput!): Expense!

  # Payments
  createExpensePayment(input: CreateExpensePaymentInput!): ExpensePayment!
  deleteExpensePayment(id: String!): IdObject!
}

# Input Types
input CreateExpenseInput {
  expenseDate: LocalDate!
  category: ExpenseCategory!
  description: String!
  amount: Float!
  currency: Currency
  notes: String
}

input CreateExpenseWithReceiptInput {
  expenseDate: LocalDate!
  category: ExpenseCategory!
  description: String!
  amount: Float!
  currency: Currency
  notes: String
  fileName: String!
  mimeType: String!
}

input CreateExpensePaymentInput {
  paymentDate: LocalDate!
  notes: String
  # One of three grouping methods:
  groupByDateRange: DateRangeInput
  groupByCategory: ExpenseCategory
  manualExpenseIds: [String!]
}

# Output Types
type Expense {
  id: String!
  employee: Employee!
  expenseDate: LocalDate!
  category: ExpenseCategory!
  description: String!
  notes: String
  amount: Float!
  currency: Currency!
  amountCHF: Float!
  exchangeRate: Float
  exchangeRateDate: LocalDate
  receiptBlobName: String
  receiptFileName: String
  receiptDownloadUrl: String  # Resolved field (presigned URL)
  extractedByAI: Boolean!
  aiConfidenceScore: Float
  status: ExpenseStatus!
  submittedAt: DateTime
  rejectedBy: Employee
  rejectionReason: String
  payment: ExpensePayment
  paidAt: DateTime
  createdAt: DateTime!
  updatedAt: DateTime!
}

type ExpenseWithUploadUrl {
  id: String!
  presignedUploadUrl: String!
  # ... other Expense fields
}

type ExtractedReceiptData {
  date: LocalDate
  amount: Float
  currency: String
  merchantName: String
  suggestedCategory: ExpenseCategory
  confidence: Float!
}
```

---

## Frontend Implementation

### Web CRM (Next.js + Mantine + pdfmake)

#### Component Structure

```
apps/web/cinformatique-crm/src/components/expenses/
├── ExpenseTable.tsx                # List with filters
├── ExpenseFormModal.tsx            # Create/edit expense
├── ExpenseDetailModal.tsx          # View expense details
├── ExpenseStatusBadge.tsx          # Status indicator
├── ExpenseReceiptUpload.tsx        # File upload + AI extraction
├── ExpenseAIExtractionPanel.tsx   # AI results with confidence
├── expense.hook.tsx                # GraphQL mutations
├── expense.fragments.graphql       # GraphQL fragments
├── expense-pdf.ts                  # PDF generation (pdfmake)
└── payments/
    ├── ExpensePaymentTable.tsx
    ├── ExpensePaymentFormModal.tsx
    ├── ExpensePaymentGrouping.tsx  # Three grouping methods
    └── expense-payment.hook.tsx
```

#### PDF Generation Pattern

```typescript
// apps/web/cinformatique-crm/src/components/expenses/expense-pdf.ts
import { TDocumentDefinitions } from 'pdfmake/interfaces';
import { ExpenseFragment } from '@nx-zero/shared/cinformatique';

export function generateExpenseReportDocumentDefinitions(
  expenses: ExpenseFragment[],
  filters: {
    dateRange?: { start: string; end: string };
    category?: string;
    employee?: string;
  }
): TDocumentDefinitions {
  return {
    content: [
      // Header
      { text: 'Rapport de Frais', style: 'header' },
      { text: `Total: ${expenses.length} frais`, style: 'subheader' },

      // Table
      {
        table: {
          headerRows: 1,
          widths: ['auto', '*', 'auto', 'auto', 'auto'],
          body: [
            ['Date', 'Catégorie', 'Description', 'Montant', 'CHF'],
            ...expenses.map(exp => [
              exp.expenseDate,
              exp.category,
              exp.description,
              `${exp.amount} ${exp.currency}`,
              exp.amountCHF.toFixed(2)
            ])
          ]
        }
      },

      // Total
      {
        text: `Total CHF: ${expenses.reduce((sum, exp) => sum + exp.amountCHF, 0).toFixed(2)}`,
        style: 'total'
      }
    ],
    styles: {
      header: { fontSize: 18, bold: true, margin: [0, 0, 0, 10] },
      subheader: { fontSize: 12, margin: [0, 0, 0, 10] },
      total: { fontSize: 14, bold: true, margin: [0, 10, 0, 0] }
    }
  };
}

// Usage in component
async function exportToPdf() {
  const docDef = generateExpenseReportDocumentDefinitions(expenses, filters);
  const pdf = await generatePdf(docDef);
  showPdfViewerModal({
    docUrl: pdf,
    fileName: `Rapport-Frais-${new Date().toISOString()}.pdf`
  });
}
```

#### Key Features
- Expense table with inline filters (date, category, status, employee)
- Create expense modal with AI extraction UI
- Receipt upload with preview
- PDF export button (generates in browser, displays in modal)
- Payment creation with 3 grouping tabs

---

### Mobile App (Expo + Tamagui)

#### Screen Structure

```
apps/mobile/cinformatique-app/src/app/(app)/expenses/
├── index.tsx                      # Expense list
├── [id].tsx                       # Expense detail
├── new.tsx                        # Create expense
├── camera.tsx                     # Receipt capture
└── components/
    ├── ExpenseCard.tsx
    ├── ExpenseForm.tsx
    ├── AIExtractionSheet.tsx      # Bottom sheet with AI results
    └── StatusBadge.tsx
```

#### Key Features
- Camera integration (`expo-image-picker`)
- AI extraction with loading state
- Form pre-filled with AI data (editable)
- File upload to Azure (presigned URL pattern)
- List with pull-to-refresh

---

## Implementation Phases

### Phase 1: Foundation (3-4 days)
- ✅ Create EdgeDB schema (Expense + ExpensePayment)
- ✅ Run migrations
- ✅ Implement repositories, services, resolvers
- ✅ Basic CRUD working
- ✅ Tests passing

### Phase 2: Currency Conversion (1 day)
- ✅ Implement Frankfurter API service
- ✅ Test multi-currency conversion
- ✅ Unit tests

### Phase 3: AI Extraction (2 days)
- ✅ Azure Document Intelligence integration
- ✅ Receipt extraction mutation
- ✅ Test with various receipt types
- ✅ Handle edge cases

### Phase 4: Web CRM (3-4 days)
- ✅ Expense table with filters
- ✅ Expense form modal with AI extraction
- ✅ Receipt upload component
- ✅ Payment creation with grouping
- ✅ PDF export (frontend)

### Phase 5: Mobile App (3-4 days)
- ✅ Expense list screen
- ✅ Camera/gallery capture
- ✅ AI extraction UI
- ✅ Expense form
- ✅ File upload

### Phase 6: Testing & Polish (2 days)
- ✅ End-to-end testing
- ✅ Performance optimization
- ✅ Documentation

**Total: 14-19 days**

---

## Technical Decisions Summary

| Feature | Implementation | Rationale |
|---------|----------------|-----------|
| Exchange Rates | Frankfurter API (no DB storage) | Free, no limits, simplified architecture |
| VAT | Store gross amounts only | Simplified model, good enough for now |
| PDF Export | Frontend (pdfmake) | Matches invoice pattern, no backend load |
| AI Extraction | Azure Document Intelligence | Pre-trained receipt model, high accuracy |
| File Storage | Azure Blob (presigned URLs) | Already configured for C Informatique |
| Data Model | Flat (single Expense entity) | Simpler, mobile-first, easier to implement |

---

## Environment Variables

```env
# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://xxx.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key_here

# Azure Storage (already configured)
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER_NAME=c-informatique

# No Frankfurter API key needed (public API)
```

---

## Dependencies

### Backend (already exists)
- `@azure/ai-form-recognizer` (v5.0.0) - Document Intelligence

### Frontend
- `pdfmake` (already exists) - PDF generation
- `@tabler/icons-react` (already exists) - Icons

---

## Open Questions

1. **AI Confidence** - Show warning if extraction <70%?
2. **Notifications** - Email/push when approved/rejected?
3. **Receipt Requirements** - Mandatory for all categories?
4. **Historical Editing** - If editing old expense, use current exchange rate?

---

## Success Criteria

- ✅ Employees can submit expenses via web and mobile
- ✅ AI extracts receipt data with >80% success rate
- ✅ Currency conversion accurate to 0.01 CHF
- ✅ Managers can approve/reject in <1 minute
- ✅ Admins can create payments with 3 grouping methods
- ✅ PDF export works with filters
- ✅ Mobile camera upload works on iOS/Android
- ✅ All quality gates pass (lint, test, build)

---

**Ready for implementation!** 🚀