# Spacesonic ERP Architecture

## Version

ERP v0.6 – Core Architecture Stable

## Purpose

Το Spacesonic ERP είναι ένα σύστημα παραγωγής, αποθήκης, αγορών και προγραμματισμού υλικών για βιομηχανική παραγωγή.

Ο βασικός στόχος είναι:

* καταγραφή παραγωγής,
* παρακολούθηση αποθέματος,
* υπολογισμός κατανάλωσης,
* προγραμματισμός αγορών,
* δημιουργία purchase orders,
* μελλοντικά MRP, work orders και capacity planning.

---

# Architecture Principle

Το ERP ακολουθεί διαχωρισμό:

```text
UI Layer
    ↓
Service Layer
    ↓
Database Layer
```

## UI Layer

Φάκελος:

```text
tabs/
```

Περιέχει μόνο Streamlit UI.

Δεν πρέπει να περιέχει:

* SQL INSERT
* SQL UPDATE
* SQL DELETE
* business logic
* inventory calculations

## Service Layer

Φάκελος:

```text
services/
```

Περιέχει:

* CRUD logic
* database writes
* audit logging
* business rules
* inventory update calls

## Database Layer

Αρχείο:

```text
db.py
```

Περιέχει μόνο τη σύνδεση με τη MySQL database.

---

# Database Model

## 1. Master Data

Οι πίνακες master data περιγράφουν βασικές οντότητες που αλλάζουν σπάνια.

### materials

Current operational master for materials.

Σήμερα χρησιμοποιείται από:

* production
* receipts
* inventory report
* dashboard
* procurement
* material search

Current fields:

```text
material_code
material_name
stock_on_hand
unit
supplier
lead_time_days
```

Decision:

```text
KEEP
```

Short-term role:

```text
Operational material master
```

Long-term role:

```text
Pure material master without stock_on_hand
```

Future change:

Το `stock_on_hand` πρέπει να φύγει μακροπρόθεσμα από τον `materials` και το stock να περάσει στο inventory layer.

---

### items

Inventory layer table.

Fields:

```text
item_id
material_code
stage_code
item_name
unit
item_type
stock_on_hand
```

Allowed item types:

```text
RAW
WIP
FINAL
```

Decision:

```text
KEEP
```

Role:

Ο πίνακας `items` δεν αντικαθιστά απλά τον `materials`.

Ο ρόλος του είναι να περιγράφει inventory objects ανά στάδιο:

```text
RAW material
WIP item
FINAL item
```

Example:

```text
0025-0373 | RAW | RAW
0025-0373 | S16 | WIP
ATRAX5-HEAD | FINAL | FINAL
```

---

### suppliers

Supplier master.

Fields:

```text
supplier_id
supplier_name
country
lead_time_days
active
```

Decision:

```text
KEEP
```

Role:

Χρησιμοποιείται για Supplier Management και μελλοντικά Purchase Orders.

---

### employees

Employee master.

Fields:

```text
employee_id
employee_name
active
```

Decision:

```text
KEEP
```

Role:

Χρησιμοποιείται σε production tracking και μελλοντικά employee planning.

---

### production_stages

Production stage master.

Decision:

```text
KEEP
```

Role:

Περιγράφει τα στάδια παραγωγής.

---

### stage_inputs

BOM input configuration.

Decision:

```text
KEEP
```

Role:

Περιγράφει ποια υλικά καταναλώνονται σε κάθε στάδιο, ανά μοντέλο.

---

### stage_outputs

BOM output configuration.

Decision:

```text
KEEP
```

Role:

Περιγράφει τι παράγεται σε κάθε στάδιο.

---

# 2. Transactions

Οι transactional πίνακες καταγράφουν γεγονότα.

## production_log

Decision:

```text
KEEP
```

Role:

Καταγραφή παραγωγής.

Contains:

```text
production_date
stage_id
model
quantity
head_count
employee_id
```

Current service:

```text
production_service.py
```

---

## receipts

Decision:

```text
KEEP
```

Role:

Καταγραφή παραλαβών / αγορών.

Current service:

```text
receipt_service.py
```

---

## purchaseorders

Decision:

```text
KEEP
```

Role:

Purchase order header.

Not fully implemented yet.

---

## purchaseorder_lines

Decision:

```text
KEEP
```

Role:

Purchase order lines.

Currently depends on:

```text
items.item_id
```

Important note:

Δεν πρέπει να υλοποιηθεί πλήρως το Purchase Order Service πριν ολοκληρωθεί η στρατηγική χρήσης του `items`.

---

## workorders

Decision:

```text
KEEP FOR FUTURE
```

Role:

Μελλοντικό production planning / work order execution.

---

# 3. Inventory

## stocktransactions

Decision:

```text
KEEP
```

Role:

Μελλοντική πηγή αλήθειας για inventory movements.

Long-term target:

```text
Receipts → stocktransactions
Production → stocktransactions
Adjustments → stocktransactions
Transfers → stocktransactions
```

---

## vw_currentstock

Decision:

```text
KEEP
```

Role:

Reporting view για current stock.

Long-term target:

Το current stock να προκύπτει από `stocktransactions`.

---

# 4. Procurement

## item_suppliers

Decision:

```text
KEEP FOR FUTURE
```

Role:

Σύνδεση υλικών/items με suppliers.

Current issue:

Ο πίνακας έχει σχεδιαστεί για `items.item_id`, αλλά το σημερινό operational ERP δουλεύει ακόμα με `materials.material_code`.

Decision:

Δεν χρησιμοποιείται ενεργά μέχρι να ολοκληρωθεί το migration στο `items`.

---

# 5. System

## audit_log

Decision:

```text
KEEP
```

Role:

Καταγραφή αλλαγών.

Used by:

* production_service
* receipt_service
* employee_service
* supplier_service

---

# Current Architecture Status

## Completed

```text
app.py cleanup
tabs separation
production_service
receipt_service
employee_service
supplier_service
procurement_service
report_service
backup v0.6
```

## Pending

```text
Purchase Order Service
Inventory Migration
Items Migration
Stocktransactions Integration
Work Orders
Capacity Planning
```

---

# Key Architecture Decisions

## Decision 1

`materials` παραμένει ο σημερινός operational material master.

## Decision 2

`items` είναι το future inventory layer και δεν πρέπει να χρησιμοποιείται πρόχειρα πριν γίνει οργανωμένο migration.

## Decision 3

`stocktransactions` θα γίνει μελλοντικά η πηγή αλήθειας για αποθέματα.

## Decision 4

Το `inventory_system_v4.py` παραμένει προσωρινά ενεργό μέχρι να ολοκληρωθεί το inventory migration.

## Decision 5

Δεν προσθέτουμε πλέον SQL μέσα στα tabs.

Όλα τα writes περνούν από services.

---

# Migration Roadmap

## Phase 1 – Completed

```text
Core UI refactoring
Services pattern
MySQL operational ERP
```

## Phase 2 – Current

```text
Supplier Management
Architecture documentation
Purchase Order preparation
```

## Phase 3 – Planned

```text
materials → items migration
stocktransactions activation
purchaseorders implementation
workorders implementation
```

## Phase 4 – Future

```text
Full MRP
Capacity Planning
Production Scheduling
Supplier Performance
ERP v1.0
```
## Milestone 0.9 – Inventory Engine

Completed:

- InventoryService V2
- Atomic Inventory Transactions
- Receipt Integration
- Current Stock View
- Transaction History
- Inventory Item Architecture