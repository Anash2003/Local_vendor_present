# Local Vendor Connecting App – Execution & Quickstart Guide

A full-stack Django website built with Django MVT, SQLite, FBVs (Functional Views), HTML, and CSS.

---

## 🚀 Running the Project

### 1. Activate Environment & Run Development Server
```bash
python manage.py runserver
```
The application will be live at: **`http://127.0.0.1:8000/`**

---

## 👥 Seeded Demonstration Accounts

Pre-populated sample data is ready in your SQLite database:

| Module / Role | Username | Password | Purpose & Notes |
|---|---|---|---|
| **Site Admin** | `admin` | `Admin@123` | Complete platform management, KYC review & approvals |
| **Verified Vendor** | `raj_plumbing` | `Vendor@123` | Approved vendor with services & availability schedules |
| **Customer** | `sneha_customer` | `Customer@123` | Can browse vendors/services and book appointments |

---

## 🛡️ Key Architectural & Security Guarantees

1. **Strictly Session-Based Authentication (NO JWT)**
   - Leverages Django's native `authenticate()`, `login()`, and `logout()` mechanisms.
   - HttpOnly session cookies with configurable expirations.
2. **5 Distinct Django Applications**
   - `accounts`: User authentication, session handling, customer & vendor registrations.
   - `customer`: Customer dashboard, service catalog, vendor explorer, booking system, personal profile.
   - `vendor`: Vendor dashboard, service management, weekly availability planner, booking orders.
   - `services`: Shared models (Categories, Services, Availability, Bookings).
   - `custom_admin`: Fully custom admin dashboard (no reliance on Django default admin).
3. **8 Core Database Models**
   - `User` (Extended with `user_type`), `CustomerProfile`, `VendorProfile`, `VendorDocument`, `ServiceCategory`, `Service`, `VendorAvailability`, `Booking`.
4. **Three Custom Decorators**
   - `@customer_required`: Ensures authenticated and valid active customer.
   - `@vendor_required`: Verifies authentication, active vendor profile, and **Approved** verification status.
   - `@admin_required`: Enforces staff + admin user permissions.
5. **Strict Vendor Verification Workflow**
   - Vendor Registration $\to$ Document Upload (UUID storage, protected access) $\to$ Pending Verification $\to$ Admin Review & Approval $\to$ Dashboard Access.
   - Pending/Rejected vendors cannot log in or view vendor features.
6. **Zero Raw SQL & Robust Ownership Checks**
   - All queries use Django ORM.
   - Every booking and profile view validates ownership (`customer=request.user.customer_profile` / `vendor=request.user.vendor_profile`).
   - Private documents can only be served via admin-authorized views (`custom_admin:view_document`).

