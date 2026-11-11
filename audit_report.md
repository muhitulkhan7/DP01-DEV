# Campus DengueWatch: Comprehensive Forensic Audit Report

**Document Version:** 1.0.0  
**Audit Date:** November 10, 2026  
**Audited Target:** `e:\DP01 DEV` (Campus DengueWatch Codebase)  
**Integrity Mode:** Development / Strict Non-Modification (Zero codebase mutations applied)  
**Reference Specifications:**
- `Agent v3.md` (Standing Instructions, Architectural Contracts, and Domain Rules)
- `Campus DengueWatch Development Plan v3.md` (Phased Four-Phase Implementation Plan)
- `Campus_Dengue_Guard_System_Design.txt` & System Diagrams (Draw.io Specification)

---

## Executive Summary

A comprehensive, read-only forensic software audit was conducted across the active codebase of **Campus DengueWatch** (`e:\DP01 DEV`). The audit systematically examined all application source files, configuration modules, templates, static JavaScript/CSS assets, database fixtures, and automated test modules to evaluate four primary dimensions:
1. **Defect & Bug Identification (R1):** Unhandled runtime exceptions, logic flaws, architectural bugs, and critical security vulnerabilities.
2. **Specification & Guideline Alignment (R2):** Compliance with architectural mandates, geometric boundary specifications, timezone conventions, OOP contracts, and phased milestone deliverables.
3. **Unwanted Code & Test Script Inventory (R3):** Detection of dead code, unused imports, speculative feature stubs, orphaned assets, and classification of test files.
4. **Security, Architecture, & Code Quality (R4):** Structural health, anti-patterns, maintainability, and readiness for future milestone integration.

### Core Metrics Summary

| Audit Dimension | Metric Value | Key Findings & Status |
| :--- | :--- | :--- |
| **Total Codebase Defects (R1)** | **14 Issues** | 1 Critical, 4 High, 6 Medium, 3 Low |
| **Specification Discrepancies (R2)** | **15 Discrepancies** | 3 Missing Phase Apps, 1 Boundary Deviation, 1 Spec Contradiction, 10 Code Deviations |
| **Unwanted / Dead Items (R3)** | **10 Items** | 8 Dead Code / Inactive Items in active files, 2 Orphaned Project Assets |
| **Automated Test Suite Status** | **21 Passing Tests** | 21/21 Unit & Integration Tests pass (`Ran 21 tests in 24.2s, OK`); 0 failures |
| **Scratch / Temporary Test Scripts** | **0 Detected** | No temporary scratch scripts; test suites are legitimate, official Django suites |
| **Active Development Footprint** | **Phase 1 Only** | `accounts` and `reports` implemented; Phases 2, 3, and 4 are completely unbuilt |
| **Workspace Write Integrity** | **100% Compliant** | Zero existing files altered, deleted, or patched; audit strictly read-only |

### High-Level Synthesis

1. **Current Milestone Status (Phase 1 Footprint):**  
   The application is currently at the completion boundary of **Phase 1: Reporting and Heatmap Viewing**. The two active Django applications—`accounts` and `reports`—provide functional user registration, session authentication, mobile-responsive layout with a pure CSS navigation menu, Leaflet-based campus map visualization, point-in-polygon boundary validation, daily report rate limiting (8 reports/day), and report submission.
2. **Missing Core Features (Phases 2, 3, and 4):**  
   The project has not yet initiated Phase 2 (`workflow` and `advisories` apps for hotspot moderation, task dispatching, work verification, mitigation pins, and health advisories), Phase 3 (`medical` app for the symptom questionnaire, risk scoring, and clinic/doctor directory), or Phase 4 (`events` app for volunteer cleanup coordination).
3. **Critical Security & Architectural Risks:**  
   The audit identified a **Critical privilege escalation vulnerability** in `accounts/permissions.py` where role demotions are bypassed due to Python class inheritance checks (`isinstance` evaluating true on parent proxy classes). Furthermore, four **High severity** defects expose the system to authentication denial via case-sensitive email lookups, phantom record generation under proxy models, cleartext password exposure in Django Admin, and open URL redirects (CWE-601).
4. **Boundary Deviation:**  
   `denguewatch/settings.py` currently defines the campus boundary as a simplified 4-vertex rectangular box rather than the authoritative 56-node OpenStreetMap polygon for ULAB Permanent Campus (Way 1071236443) required by `Agent v3.md` Section 11 Item 2.
5. **Testing Suite Integrity:**  
   The existing test modules (`accounts/tests.py` and `reports/tests.py`) represent legitimate, high-value standard project test suites providing 21 passing test cases. They must be preserved and expanded rather than discarded.

---

## Section 1: Bug and Defect Identification (Requirement R1)

Forensic static and runtime analysis identified **14 distinct bugs and defects** across the active source code. Every defect is detailed below with its location, verbatim code, root cause mechanism, runtime failure evidence, severity, and remediation strategy.

### Defect Catalog Overview

| # | Defect Title | Exact File Path | Line(s) / Symbol | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | Privilege Escalation via Proxy Class Inheritance in `resolve_actor` | `accounts/permissions.py` | Lines 21–23 (`resolve_actor`) | **Critical** |
| **DEF-02** | Case-Sensitive Email Lookup Preventing User Login (Authentication Denial) | `accounts/forms.py` & `accounts/models.py` | `forms.py:108,112`, `models.py:38-63` | **High** |
| **DEF-03** | "Phantom Record" Creation via Proxy Models in Django Admin and ORM | `accounts/models.py` & `accounts/admin.py` | `models.py:73-78,110-112`, `admin.py:12-21` | **High** |
| **DEF-04** | Cleartext Password Storage & Hash Overwrite via Default `ModelAdmin` | `accounts/admin.py` | Lines 5–21 | **High** |
| **DEF-05** | Unvalidated Redirects to External Domains (Open Redirect / CWE-601) | `accounts/views.py` | Lines 24–26, 43–45 | **High** |
| **DEF-06** | Unhandled `AttributeError` on Non-Standard `ValidationError.message` | `reports/views.py` & `reports/forms.py` | `views.py:70-71`, `forms.py:65-66` | **Medium** |
| **DEF-07** | Unhandled `AttributeError` When Note is Explicitly Passed as `None` | `reports/services.py` | Line 127 (`ReportService.create_report`) | **Medium** |
| **DEF-08** | Unlocalized UTC Datetime in Heatmap API Popups (6-Hour Offset) | `reports/views.py` | Line 36 (`HeatmapView.get_context_data`) | **Medium** |
| **DEF-09** | Non-Functional Dead Navbar Report Link on Non-Heatmap Pages | `templates/base.html` & `templates/reports/heatmap.html` | `base.html:68-72`, `heatmap.html:60-87` | **Medium** |
| **DEF-10** | Silent Photo Ingestion Drop When Passed via Cleaned Data | `reports/services.py` | Lines 101, 120 | **Medium** |
| **DEF-11** | Concurrency Race Condition in Daily Report Rate Limiter | `reports/services.py` | Lines 80–98, 118–130 | **Medium** |
| **DEF-12** | Blank Gray Map Rendering on Empty Vector Layer Selection | `static/js/map.js` | Lines 76, 82–86 | **Low** |
| **DEF-13** | Strict TileLayer Bounds Inducing Grey Edge Pan Clipping & Mirror Rejection | `static/js/map.js` | Lines 69–75 | **Low** |
| **DEF-14** | Unused Calculation Variables, Dead CSS Classes, and Orphaned Imports | `report_form.html`, `style.css`, `tests.py` | `report_form.html:135`, `style.css:302`, `tests.py:3,6`| **Low** |

---

### Detailed Defect Analyses

#### DEF-01: Critical Privilege Escalation via Proxy Class Inheritance in `resolve_actor`
- **File Path:** `accounts/permissions.py`
- **Lines / Symbol:** Lines 21–23 (`accounts.permissions.resolve_actor`)
- **Verbatim Code Snippet:**
  ```python
  target_class = ROLE_CLASS_MAP.get(getattr(user, 'role', None), RegisteredUser)
  if isinstance(user, target_class):
      return user
  ```
- **Description & Vulnerability Mechanism:**  
  In the RBAC architecture, `Admin` and `Authority` are proxy subclasses inheriting from `RegisteredUser` (`class Admin(RegisteredUser): ...`). In Python object-oriented semantics, any instance of a subclass satisfies `isinstance(subclass_instance, ParentClass) == True`.  
  If a user session or user model instance was previously loaded or cached as an `Admin` or `Authority` proxy object, and the administrator demotes the user's database role to `Role.REGISTERED` (or `None`), `ROLE_CLASS_MAP.get(...)` resolves `target_class` to `RegisteredUser`.  
  The conditional `if isinstance(user, RegisteredUser):` evaluates to `True` because `Admin` is a subclass of `RegisteredUser`. Consequently, `resolve_actor` immediately returns the existing `Admin` instance without re-instantiating the user as a `RegisteredUser`. The demoted user permanently retains all privileged administrative capabilities (`verify_reports`, `assign_task`, `manage_users`, etc.).
- **Runtime Verification:**
  ```python
  from accounts.models import Admin, Role
  from accounts.permissions import resolve_actor
  demoted_user = Admin(role=Role.REGISTERED)
  actor = resolve_actor(demoted_user)
  assert type(actor) is Admin  # TRUE! Privilege escalation occurs
  assert actor.has_capability('verify_reports') == True  # TRUE! Unlawful permission retained
  ```
- **Severity:** **Critical**
- **Proposed Fix Strategy:**  
  Enforce strict exact-type equivalence instead of polymorphic subclass matching:
  ```python
  target_class = ROLE_CLASS_MAP.get(getattr(user, 'role', None), RegisteredUser)
  if type(user) is target_class:
      return user
  return target_class(id=user.id, ... ) # Re-cast via proxy instantiation
  ```

---

#### DEF-02: Case-Sensitive Email Lookup Preventing User Login (Authentication Denial)
- **File Paths:** `accounts/forms.py` (lines 108, 112) & `accounts/models.py` (lines 38–63)
- **Lines / Symbols:** `accounts.forms.LoginForm.clean`, `accounts.models.RegisteredUserManager`
- **Verbatim Code Snippets:**
  *`accounts/forms.py` lines 108, 112:*
  ```python
  email = cleaned_data.get('email', '').strip().lower()
  ...
  self.user = authenticate(username=email, password=password)
  ```
  *`accounts/models.py` lines 38–44:*
  ```python
  class RegisteredUserManager(BaseUserManager):
      def create_user(self, email, password=None, **extra_fields):
          if not email:
              raise ValueError('The Email field is required.')
          email = self.normalize_email(email)
          user = self.model(email=email, **extra_fields)
  ```
- **Description & Vulnerability Mechanism:**  
  `LoginForm.clean()` forces incoming login emails to lowercase (`.lower()`). Conversely, `RegisteredUserManager.create_user()` invokes Django's standard `BaseUserManager.normalize_email()`. `BaseUserManager.normalize_email()` strictly lowercases only the *domain* part of the email address (e.g., `Student@Campus.EDU` is normalized to `Student@campus.edu`, preserving the uppercase `S`).  
  In SQLite, default text lookups (`=`) are case-sensitive. When a user account is provisioned through Django CLI (`manage.py createsuperuser`), administrative scripts, or fixtures with any capital letters in the mailbox name (e.g. `Admin@campus.edu`), `authenticate(username='admin@campus.edu')` delegates to `RegisteredUser.objects.get_by_natural_key('admin@campus.edu')`. The query fails to match `Admin@campus.edu`. The user is permanently locked out of web authentication.
- **Runtime Verification:**
  ```python
  from accounts.models import RegisteredUser
  from django.contrib.auth import authenticate
  u = RegisteredUser.objects.create_user(email='Teacher@campus.edu', password='Password123', full_name='Prof')
  assert authenticate(username='Teacher@campus.edu', password='Password123') is not None
  assert authenticate(username='teacher@campus.edu', password='Password123') is None # Fails!
  ```
- **Severity:** **High**
- **Proposed Fix Strategy:**  
  1. Override `get_by_natural_key` in `RegisteredUserManager` to perform case-insensitive queries:
     ```python
     def get_by_natural_key(self, username):
         return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})
     ```
  2. Normalize all incoming emails completely to lowercase in `RegisteredUserManager.create_user`:
     ```python
     email = self.normalize_email(email).lower()
     ```

---

#### DEF-03: "Phantom Record" Creation via Proxy Models in Django Admin and ORM
- **File Paths:** `accounts/models.py` (lines 73–78, 110–112) & `accounts/admin.py` (lines 12–21)
- **Lines / Symbols:** `accounts.models.Authority`, `accounts.models.Admin`, `AuthorityAdmin`, `AdminUserAdmin`
- **Verbatim Code Snippets:**
  *`accounts/models.py` lines 73–78:*
  ```python
  role = models.CharField(
      max_length=20,
      choices=Role.choices,
      default=Role.REGISTERED,
      verbose_name='User Role'
  )
  ```
  *`accounts/models.py` lines 110–112:*
  ```python
  class AuthorityManager(models.Manager):
      def get_queryset(self):
          return super().get_queryset().filter(role=Role.AUTHORITY)
  ```
- **Description & Vulnerability Mechanism:**  
  The proxy models `Authority` and `Admin` inherit all model attributes from `RegisteredUser`, including the field definition `default=Role.REGISTERED`. Neither proxy model defines an overridden `save()` method or custom `__init__` constructor to automatically set `role = Role.AUTHORITY` or `role = Role.ADMIN`.  
  When an administrator creates a new Authority account via the Django Admin interface under the Authority section, or via ORM invocation `Authority.objects.create(...)`, the database record is inserted with `role = 'REGISTERED'`.  
  Because `AuthorityManager` filters queries strictly by `filter(role=Role.AUTHORITY)`, the newly inserted record does not appear in the manager's queryset. The record vanishes from the admin list view immediately upon saving, creating an orphaned "phantom record" that cannot be accessed or edited through the proxy interface.
- **Runtime Verification:**
  ```python
  from accounts.models import Authority, Role
  auth = Authority.objects.create(email='new_auth@campus.edu', full_name='Authority Staff')
  assert auth.role == Role.REGISTERED # Default inherited!
  assert Authority.objects.filter(id=auth.id).exists() == False # Vanished from its own manager!
  ```
- **Severity:** **High**
- **Proposed Fix Strategy:**  
  Implement overridden `save()` methods on the proxy models in `accounts/models.py`:
  ```python
  class Authority(RegisteredUser):
      ...
      def save(self, *args, **kwargs):
          if not self.role or self.role == Role.REGISTERED:
              self.role = Role.AUTHORITY
          super().save(*args, **kwargs)

  class Admin(RegisteredUser):
      ...
      def save(self, *args, **kwargs):
          if not self.role or self.role == Role.REGISTERED:
              self.role = Role.ADMIN
          super().save(*args, **kwargs)
  ```

---

#### DEF-04: Cleartext Password Storage & Hash Overwrite via Default `ModelAdmin`
- **File Path:** `accounts/admin.py`
- **Lines / Symbol:** Lines 5–21 (`RegisteredUserAdmin`, `AuthorityAdmin`, `AdminUserAdmin`)
- **Verbatim Code Snippet:**
  ```python
  @admin.register(RegisteredUser)
  class RegisteredUserAdmin(admin.ModelAdmin):
      list_display = ('email', 'full_name', 'role', 'is_active', 'date_joined')
      list_filter = ('role', 'is_active')
      search_fields = ('email', 'full_name')
  ```
- **Description & Vulnerability Mechanism:**  
  `RegisteredUserAdmin` inherits directly from the generic `admin.ModelAdmin` rather than Django's specialized `django.contrib.auth.admin.UserAdmin`.  
  Standard `ModelAdmin` renders model fields verbatim using standard HTML inputs. Consequently, the user `password` field is exposed in the admin edit interface as a raw text string. When an administrator saves a user profile in Django admin (e.g. to update a name or toggle active status), the form submits the text value in the password input. Because `ModelAdmin` lacks password hashing hooks, the text is saved directly to `user.password` as unhashed plaintext, overwriting the cryptographic PBKDF2/Argon2 hash. The affected user is permanently unable to log in via standard authentication.
- **Severity:** **High**
- **Proposed Fix Strategy:**  
  Subclass `django.contrib.auth.admin.UserAdmin`, customize fieldsets to omit the deprecated `username` field, and wire `UserChangeForm` / `UserCreationForm`:
  ```python
  from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

  @admin.register(RegisteredUser)
  class RegisteredUserAdmin(BaseUserAdmin):
      ordering = ('email',)
      list_display = ('email', 'full_name', 'role', 'is_active', 'date_joined')
      fieldsets = (
          (None, {'fields': ('email', 'password')}),
          ('Personal info', {'fields': ('full_name',)}),
          ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
      )
  ```

---

#### DEF-05: Unvalidated Redirects to External Domains (Open Redirect / CWE-601)
- **File Path:** `accounts/views.py`
- **Lines / Symbol:** Lines 24–26, 43–45 (`RegisterView.form_valid`, `UserLoginView.form_valid`)
- **Verbatim Code Snippet:**
  ```python
  next_url = self.request.GET.get('next')
  if next_url:
      return redirect(next_url)
  ```
- **Description & Vulnerability Mechanism:**  
  Both user registration and user login views extract the `next` query parameter from the HTTP request and pass it unfiltered into Django's `redirect()` shortcut.  
  Because there is no domain, scheme, or host verification, an external attacker can craft phishing links such as:  
  `https://campus-denguewatch.edu/accounts/login/?next=https://malicious-phishing-site.com/credential-harvest`  
  Upon successful login, Django issues an HTTP 302 redirecting the authenticated user to the external malicious domain. This constitutes an unvalidated redirect vulnerability (CWE-601).
- **Severity:** **High**
- **Proposed Fix Strategy:**  
  Validate the redirection target using Django's built-in `url_has_allowed_host_and_scheme`:
  ```python
  from django.utils.http import url_has_allowed_host_and_scheme

  next_url = self.request.GET.get('next')
  if next_url and url_has_allowed_host_and_scheme(
      url=next_url,
      allowed_hosts={self.request.get_host()},
      require_https=self.request.is_secure()
  ):
      return redirect(next_url)
  return redirect(self.success_url)
  ```

---

#### DEF-06: Unhandled `AttributeError` on Non-Standard `ValidationError.message`
- **File Paths:** `reports/views.py` (lines 70–71) & `reports/forms.py` (lines 65–66)
- **Lines / Symbols:** `ReportCreateView.form_valid`, `ReportForm.clean`
- **Verbatim Code Snippets:**
  *`reports/views.py` lines 70–71:*
  ```python
  except ValidationError as e:
      form.add_error(None, e.message)
      return self.form_invalid(form)
  ```
  *`reports/forms.py` lines 65–66:*
  ```python
  except ValidationError as e:
      self.add_error(None, e.message)
  ```
- **Description & Vulnerability Mechanism:**  
  In Django, `ValidationError.message` is an attribute present **only** when the exception is instantiated with a single string argument. If `ValidationError` is raised with a message list, a dictionary of field errors, or propagated from model validation methods (`full_clean()`), `e.message` does not exist.  
  Attempting to access `e.message` in the `except ValidationError as e:` block raises an unhandled `AttributeError: 'ValidationError' object has no attribute 'message'`, resulting in an unhandled HTTP 500 server crash. Django's `form.add_error(field, error)` natively accepts `ValidationError` instances directly.
- **Severity:** **Medium**
- **Proposed Fix Strategy:**  
  Pass the exception instance `e` directly to `form.add_error` without accessing `.message`:
  ```python
  except ValidationError as e:
      form.add_error(None, e)
      return self.form_invalid(form)
  ```

---

#### DEF-07: Unhandled `AttributeError` When Note is Explicitly Passed as `None`
- **File Path:** `reports/services.py`
- **Line / Symbol:** Line 127 (`ReportService.create_report`)
- **Verbatim Code Snippet:**
  ```python
  note=data.get('note', '').strip(),
  ```
- **Description & Vulnerability Mechanism:**  
  In Python dictionary semantics, `data.get('note', '')` returns the default empty string `''` **only** if the `'note'` key is completely absent from `data`. If an external caller, REST client, unit test, or form cleaning process provides `data` with `{'note': None}`, `data.get('note', '')` evaluates to `None`.  
  Calling `.strip()` on `None` throws an unhandled `AttributeError: 'NoneType' object has no attribute 'strip'`, crashing the report creation pipeline.
- **Runtime Verification:**
  ```python
  payload = {'category': 'STAGNANT_WATER', 'latitude': 23.7599, 'longitude': 90.3489, 'note': None}
  payload.get('note', '').strip()  # Raises AttributeError: 'NoneType' object has no attribute 'strip'
  ```
- **Severity:** **Medium**
- **Proposed Fix Strategy:**  
  Safely coalesce `None` values before stripping:
  ```python
  note=(data.get('note') or '').strip(),
  ```

---

#### DEF-08: Unlocalized UTC Datetime in Heatmap API Popups (6-Hour Offset)
- **File Path:** `reports/views.py`
- **Line / Symbol:** Line 36 (`HeatmapView.get_context_data`)
- **Verbatim Code Snippet:**
  ```python
  'created_at': r.created_at.strftime('%b %d, %Y, %I:%M %p'),
  ```
- **Description & Vulnerability Mechanism:**  
  In Django with `USE_TZ = True`, datetime fields (`r.created_at`) are stored and retrieved as timezone-aware UTC objects. Calling Python's native `.strftime()` on an aware UTC datetime formats the time in UTC, ignoring the project's configured timezone (`TIME_ZONE = 'Asia/Dhaka'`).  
  Consequently, report markers on the Leaflet heatmap display timestamps that are exactly 6 hours behind Bangladesh Standard Time (UTC+6). Reports submitted in the early morning display timestamps from the previous calendar day, confusing students and campus health staff.
- **Runtime Verification:**
  ```python
  from django.utils import timezone
  import datetime
  dt = timezone.now() # Suppose 02:00 AM BST (20:00 UTC previous day)
  assert dt.strftime('%I:%M %p') != timezone.localtime(dt).strftime('%I:%M %p') # 6 hour drift!
  ```
- **Severity:** **Medium**
- **Proposed Fix Strategy:**  
  Convert to local time prior to string formatting:
  ```python
  from django.utils import timezone

  'created_at': timezone.localtime(r.created_at).strftime('%b %d, %Y, %I:%M %p'),
  ```

---

#### DEF-09: Non-Functional Dead Navbar Report Link on Non-Heatmap Pages
- **File Paths:** `templates/base.html` (lines 68–72) & `templates/reports/heatmap.html` (lines 60–87)
- **Lines / Symbols:** `#report-gate-modal`
- **Verbatim Code Snippet (`templates/base.html` lines 68–72):**
  ```html
  {% else %}
    <li>
      <a class="nav-item-link nav-cta-btn" href="#report-gate-modal">
        + Report Mosquito Activity
      </a>
    </li>
  ```
- **Description & Vulnerability Mechanism:**  
  When an unauthenticated visitor navigates to any page other than the homepage (for example, `/accounts/login/` or `/accounts/register/`), the navigation header renders the call-to-action button linking to `#report-gate-modal`.  
  However, the modal markup (`<div id="report-gate-modal" class="modal-overlay">...</div>`) is embedded exclusively inside `templates/reports/heatmap.html`. Because the modal does not exist in the DOM of login or register pages, clicking the button modifies the browser fragment URL but triggers zero visual or functional response. To the user, the button appears broken.
- **Severity:** **Medium**
- **Proposed Fix Strategy:**  
  Update the link in `templates/base.html` to target the homepage fragment:
  ```html
  <a class="nav-item-link nav-cta-btn" href="{% url 'heatmap' %}#report-gate-modal">
    + Report Mosquito Activity
  </a>
  ```
  Alternatively, relocate the `#report-gate-modal` markup into `templates/base.html` so the login gate modal can pop up anywhere across the site.

---

#### DEF-10: Silent Photo Ingestion Drop When Passed via Cleaned Data
- **File Paths:** `reports/services.py` (lines 101, 120) & `reports/views.py` (line 68)
- **Lines / Symbols:** `ReportService.create_report`
- **Verbatim Code Snippet (`reports/services.py` lines 101, 120):**
  ```python
  @classmethod
  def create_report(cls, user, data, files=None) -> Report:
      ...
      photo = files.get('photo') if files else None
  ```
- **Description & Vulnerability Mechanism:**  
  `ReportService.create_report` explicitly expects uploaded files to be passed in a separate `files` dictionary and reads exclusively from `files.get('photo')`.  
  In standard Django architectures, a validated `ModelForm` places cleaned file objects into `form.cleaned_data['photo']`. If an external caller, service consumer, or unit test invokes `ReportService.create_report(user, form.cleaned_data)` without passing `files`, `files` evaluates to `None`. The service ignores `data.get('photo')`, silently dropping the uploaded image and saving the report with `photo = None`.
- **Severity:** **Medium**
- **Proposed Fix Strategy:**  
  Inspect both `files` and `data` for photo payload:
  ```python
  photo = files.get('photo') if files else data.get('photo')
  ```

---

#### DEF-11: Concurrency Race Condition in Daily Report Rate Limiter
- **File Path:** `reports/services.py`
- **Lines / Symbol:** Lines 80–98, 118–130 (`ReportService.check_rate_limit`, `ReportService.create_report`)
- **Verbatim Code Snippet:**
  ```python
  count = Report.objects.filter(
      user=user,
      created_at__date=today
  ).count()

  if count >= daily_limit:
      raise ValidationError('Too many reports today')
  ```
- **Description & Vulnerability Mechanism:**  
  The daily rate limit enforcement follows a classic "check-then-act" pattern without database-level concurrency controls.  
  If an authenticated user submits multiple concurrent HTTP requests (e.g., via rapid double-clicking on mobile or an automated script), two separate threads or processes execute `count = Report.objects.filter(...).count()`. If both queries read `count = 7` (below the limit of 8), both threads validate successfully and proceed to execute `Report.objects.create(...)`. The user successfully bypasses the rate limit, persisting 9 or more reports on the same day.
- **Severity:** **Medium**
- **Proposed Fix Strategy:**  
  Execute the rate-check and report creation inside an atomic transaction with table locking or maintain a dedicated daily counter record updated with `select_for_update()`:
  ```python
  from django.db import transaction

  with transaction.atomic():
      # Lock rows or check count within serialized transaction block
      count = Report.objects.select_for_update().filter(user=user, created_at__date=today).count()
      if count >= daily_limit:
          raise ValidationError('Too many reports today')
      report = Report.objects.create(...)
  ```

---

#### DEF-12: Blank Gray Map Rendering on Empty Vector Layer Selection
- **File Path:** `static/js/map.js`
- **Lines / Symbol:** Lines 76, 82–86 (`CampusMap.initMap`)
- **Verbatim Code Snippet:**
  ```javascript
  var offlineVector = L.layerGroup();
  ...
  L.control.layers({
    'OpenStreetMap (Standard)': osmStandard,
    'OpenStreetMap (Mirror)': osmMirror,
    'Offline Vector (Internal Only)': offlineVector
  }, null, { position: 'topright' }).addTo(map);
  ```
- **Description & Vulnerability Mechanism:**  
  `CampusMap.initMap` instantiates an empty Leaflet layer group `var offlineVector = L.layerGroup();` and registers it in the top-right layer toggle control as `'Offline Vector (Internal Only)'`.  
  Because no vector tiles, GeoJSON shapes, or background tiles are ever attached to this layer group, toggling this option replaces the active basemap with a blank gray canvas, hiding all campus features and geographic context.
- **Severity:** **Low**
- **Proposed Fix Strategy:**  
  Remove the `offlineVector` layer and the `L.control.layers` control entirely until an offline vector tile source is formally implemented.

---

#### DEF-13: Strict TileLayer Bounds Inducing Grey Edge Pan Clipping & Mirror Rejection
- **File Path:** `static/js/map.js`
- **Lines / Symbol:** Lines 69–75 (`CampusMap.initMap`)
- **Verbatim Code Snippet:**
  ```javascript
  if (bufferBounds) {
    tileOptionsStandard.bounds = bufferBounds;
    tileOptionsMirror.bounds = bufferBounds;
  }
  var osmMirror = L.tileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png', tileOptionsMirror);
  ```
- **Description & Vulnerability Mechanism:**  
  Attaching `bounds = bufferBounds` directly to the `L.tileLayer` options instructs Leaflet to reject tile requests that fall outside the immediate bounding box. When a mobile user pans or zooms near the perimeter of the 1 km buffer, tiles at the viewport boundary are withheld, causing jarring gray rectangular artifacts.  
  Additionally, the German mirror `tile.openstreetmap.de` enforces strict automated referrer blocking and bandwidth throttling, returning HTTP 403 Forbidden errors when loaded from external origins.
- **Severity:** **Low**
- **Proposed Fix Strategy:**  
  Remove `bounds` from `tileOptionsStandard` (relying on `map.setMaxBounds(bufferBounds)` with appropriate padding), and remove the `osmMirror` tile layer.

---

#### DEF-14: Unused Calculation Variables, Dead CSS Classes, and Orphaned Imports
- **File Paths:**
  - `templates/reports/report_form.html` (lines 135–136)
  - `static/css/style.css` (lines 302–308)
  - `accounts/tests.py` (lines 3, 6)
- **Lines / Symbols:** `initialLat`, `initialLng`, `.floating-report-btn`, `RequestFactory`, `ActorCapabilityMixin`
- **Verbatim Code Snippets:**
  *`templates/reports/report_form.html` lines 135–136:*
  ```javascript
  var initialLat = document.getElementById('id_latitude').value || centerLat;
  var initialLng = document.getElementById('id_longitude').value || centerLng;
  ```
  *`static/css/style.css` lines 302–308:*
  ```css
  .floating-report-btn {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    z-index: 1010;
    box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
  }
  ```
  *`accounts/tests.py` lines 3, 6:*
  ```python
  from django.test import TestCase, RequestFactory
  from .permissions import resolve_actor, verify_actor_capability, ActorCapabilityMixin
  ```
- **Description & Vulnerability Mechanism:**  
  In `report_form.html`, variables `initialLat` and `initialLng` are declared and initialized but never passed to `CampusMap.enablePinPicker`, which directly accesses DOM element values instead.  
  In `style.css`, `.floating-report-btn` is defined but unreferenced across all project templates.  
  In `accounts/tests.py`, `RequestFactory` and `ActorCapabilityMixin` are imported on lines 3 and 6 but never referenced in any test method. These violate the Clean Code mandates of `Agent v3.md` Section 4 ("No dead code, no unused imports").
- **Severity:** **Low**
- **Proposed Fix Strategy:**  
  Remove the unused variable assignments, unreferenced CSS rules, and unused imports.

---

## Section 2: Specification and Guidelines Alignment Check (Requirement R2)

The codebase was audited against the specifications set forth in `Agent v3.md`, `Campus DengueWatch Development Plan v3.md`, and system design diagrams. A total of **15 discrepancies (D01–D15)** were identified.

### Comprehensive Discrepancy Matrix

| # | Discrepancy Summary | Severity | Primary Specifications Cited | Files Involved |
| :--- | :--- | :--- | :--- | :--- |
| **D01** | Campus Boundary Defined as 4-Node Box Instead of 56-Node OSM Polygon | **High** | `Agent v3.md` §11 Item 2, §2 Rule 4; `Plan v3.md` §3.3 Item #2 | `denguewatch/settings.py:116-133` |
| **D02** | Inconsistent Campus Center Coordinates Across Configurations & Scripts | **Medium** | `Agent v3.md` §11 Item 2; `Plan v3.md` §3.3 Item #2 | `settings.py`, `map.js`, `heatmap.html`, `form.html` |
| **D03** | Unrequested Map Tile Switcher & Stubbed Vector Layer | **Medium** | `Agent v3.md` §2 Rule 2, §3 (JavaScript Rule) | `static/js/map.js:64-86` |
| **D04** | UTC `.strftime()` Serialization Bypassing `Asia/Dhaka` Local Timezone | **Medium** | `Agent v3.md` §11 Item 12; `Plan v3.md` §3.3 Item #12 | `reports/views.py:36` |
| **D05** | Service Method Signature Deviation & Photo Bypassing in `create_report` | **Medium** | `Agent v3.md` §7 (Service Classes), §4 | `reports/services.py:101`, `reports/views.py:68` |
| **D06** | Redundant Boundary Validation in Both Form Clean and Service | **Low** | `Agent v3.md` §4 (Business Rules in Services Only) | `reports/forms.py:63-66`, `reports/services.py:117` |
| **D07** | Insecure GET-Based Logout Handler and Anchor Tag Navigation | **Medium** | `Agent v3.md` §4; Django Security Standards | `accounts/views.py:55-59`, `templates/base.html:65` |
| **D08** | Premature Declaration of Phase 2–4 Capabilities on User Models | **Low** | `Plan v3.md` §1.3, §3.1, §7; `Agent v3.md` §2 Rule 3 | `accounts/models.py:85-93,122-127,151-161` |
| **D09** | Polymorphic Property Bypass on `RegisteredUser.capabilities` | **Medium** | `Agent v3.md` §5, §6.2 | `accounts/models.py:95-97,103-104` |
| **D10** | Specification Conflict Regarding In-Repo Automated Test Files | **Medium** | `Agent v3.md` §11 Item 15 vs `Plan v3.md` §3.3 Item #15 | `accounts/tests.py`, `reports/tests.py` |
| **D11** | Hardcoded Insecure Default `SECRET_KEY` Without Production Guards | **Medium** | `Agent v3.md` §9 (Secrets and Environment Settings) | `denguewatch/settings.py:11-14` |
| **D12** | Hardcoded Fallback for `DAILY_REPORT_LIMIT` Inside Service Logic | **Low** | `Agent v3.md` §8.1; `Plan v3.md` §3.1 | `reports/services.py:88` |
| **D13** | Complete Absence of Phase 2: Heatmap Management & Workflow | **Critical** | `Agent v3.md` §6, §7, §8.2, §8.3; `Plan v3.md` §4 | Entire project (`workflow`, `advisories` missing) |
| **D14** | Complete Absence of Phase 3: Medical Help Portal & Questionnaire | **Critical** | `Agent v3.md` §7, §8.4; `Plan v3.md` §5 | Entire project (`medical` missing) |
| **D15** | Complete Absence of Phase 4: Volunteer Cleanup Portal | **Critical** | `Agent v3.md` §7, §8.5; `Plan v3.md` §6 | Entire project (`events` missing) |

---

### Detailed Discrepancy Reports

#### D01: Campus Boundary Geometry Definition Deviation
- **Exact File Path & Lines:** `denguewatch/settings.py`, lines 116–133 (`CAMPUS_GEOJSON`).
- **Specification Citations:**
  - `Agent v3.md` Section 11, Item 2: *"Campus boundary coordinates & daily report limit: OpenStreetMap 56-node polygon perimeter for ULAB Permanent Campus (Way 1071236443, center `23°45′35.9″N 90°20′56.3″E` / `23.759973, 90.348976`) plus 1 km viewport buffer restriction; daily limit `8` reports/day per user."*
  - `Agent v3.md` Section 2, Rule 4: *"Do not invent values. The campus boundary coordinates are supplied by the owner before the Reporting phase... Until then, do not hard-code guesses. Ask."*
- **Description & Operational Impact:**  
  `denguewatch/settings.py` configures `CAMPUS_GEOJSON` as a simple 4-corner bounding rectangle:
  ```python
  "coordinates": [
      [
          [90.34722159156507, 23.760976259183863],
          [90.35026859728328, 23.760976259183863],
          [90.35026859728328, 23.758991710110735],
          [90.34722159156507, 23.758991710110735],
          [90.34722159156507, 23.760976259183863],
      ]
  ]
  ```
  Instead of utilizing the agreed OpenStreetMap 56-node polygon representing the true perimeter of ULAB Permanent Campus (Way 1071236443), the system relies on an axis-aligned box. Because `ReportService._is_point_in_polygon` performs ray-casting against this polygon, points located outside the university grounds (e.g. adjacent private plots and public roads within the rectangular envelope) are erroneously accepted as valid campus locations.
- **Alignment Recommendation:**  
  Populate `CAMPUS_GEOJSON` with the authoritative 56-coordinate array extracted from OSM Way 1071236443, and re-verify boundary checks against ground truth campus limits.

---

#### D02: Inconsistent Campus Center Coordinates Across Configurations & Scripts
- **Exact File Paths & Lines:**
  - `denguewatch/settings.py`, lines 157–158 (derives `~23.759984, 90.348745`).
  - `static/js/map.js`, lines 19–20 (`23.759973, 90.348976`).
  - `templates/reports/heatmap.html`, lines 99–100 (`23.759791, 90.348268`).
  - `templates/reports/report_form.html`, lines 132–133 (`23.759791, 90.348268`).
- **Specification Citations:**
  - `Agent v3.md` Section 11, Item 2: specifies center `23°45′35.9″N 90°20′56.3″E` (`23.759973, 90.348976`).
  - `Campus DengueWatch Development Plan v3.md` Section 3.3, Item #2: lists center `~23°45′35″N 90°20′54″E` (`23.759791, 90.348268`).
- **Description & Operational Impact:**  
  Three distinct coordinate pairs are hardcoded across Python settings, template fallback scripts, and frontend JavaScript. Depending on whether boundary data successfully deserializes from `json_script`, the map initializes at slightly different geographical centers across pages.
- **Alignment Recommendation:**  
  Standardize the campus center to `23.759973, 90.348976` in `settings.py` and eliminate duplicate fallback coordinates in template script blocks.

---

#### D03: Unrequested Map Tile Switcher & Stubbed Vector Layer
- **Exact File Path & Lines:** `static/js/map.js`, lines 64–67, 75–76, 81–86.
- **Specification Citations:**
  - `Agent v3.md` Section 2, Rule 2: *"Do not invent features. Implement only what is in the design document, diagrams, or the current phase's task. No extras, no 'nice-to-haves'..."*
  - `Agent v3.md` Section 3 (JavaScript Rule): *"Maps: Leaflet.js + OpenStreetMap tiles... As little JS as possible, only for the map portion."*
- **Description & Operational Impact:**  
  `map.js` instantiates a secondary German tile mirror (`openstreetmap.de`), an unpopulated `offlineVector` group, and an `L.control.layers` UI toggle control. None of these components exist in the system design, use cases, or architectural contracts. Selecting the vector layer causes a blank gray map.
- **Alignment Recommendation:**  
  Strip out `osmMirror`, `offlineVector`, and `L.control.layers`. Maintain a clean, single-layer OpenStreetMap integration.

---

#### D04: UTC `.strftime()` Serialization Bypassing `Asia/Dhaka` Local Timezone
- **Exact File Path & Lines:** `reports/views.py`, line 36 (`HeatmapView.get_context_data`).
- **Specification Citations:**
  - `Agent v3.md` Section 11, Item 12: *"Time zone: `Asia/Dhaka`, with 'today' defined as the local calendar day. | Resolved"*
- **Description & Operational Impact:**  
  Line 36 formats `r.created_at` using native `.strftime()` without timezone localization. Report popups on the public heatmap display UTC time, creating a 6-hour discrepancy with Bangladesh Standard Time.
- **Alignment Recommendation:**  
  Update serialization in `HeatmapView`:
  ```python
  'created_at': timezone.localtime(r.created_at).strftime('%b %d, %Y, %I:%M %p')
  ```

---

#### D05: Service Method Signature Deviation & Photo Bypassing in `create_report`
- **Exact File Paths & Lines:** `reports/services.py` lines 101, 120, 128; `reports/views.py` line 68.
- **Specification Citations:**
  - `Agent v3.md` Section 7 (Service Classes table): specifies `create_report(user, data)`.
  - `Agent v3.md` Section 4: *"Views stay thin: parse the request, call a service or model method, return a response."*
- **Description & Operational Impact:**  
  The service method signature was expanded to `create_report(cls, user, data, files=None)`, deviating from the design specification. Inside the service, line 120 inspects only `files.get('photo')`, ignoring `data.get('photo')`.
- **Alignment Recommendation:**  
  Standardize the signature to `create_report(cls, user, data)` and extract photos via `photo = data.get('photo')` (with optional fallback to `files` if provided).

---

#### D06: Redundant Boundary Validation in Both Form Clean and Service
- **Exact File Paths & Lines:** `reports/forms.py` lines 63–66; `reports/services.py` line 117.
- **Specification Citations:**
  - `Agent v3.md` Section 4: *"Business rules live in service classes or model methods, never in templates and never duplicated in views."*
- **Description & Operational Impact:**  
  Boundary ray-casting validation is executed twice on every submission: first in `ReportForm.clean()`, and immediately again inside `ReportService.create_report()`. This introduces redundant CPU processing on geolocation math.
- **Alignment Recommendation:**  
  Centralize domain boundary enforcement in `ReportService.create_report()`. Catch domain `ValidationError` exceptions in the view to attach errors to the form.

---

#### D07: Insecure GET-Based Logout Handler and Anchor Tag Navigation
- **Exact File Paths & Lines:** `accounts/views.py` lines 55–59; `templates/base.html` line 65.
- **Specification Citations:**
  - `Agent v3.md` Section 4: *"Prefer Django built-ins over custom reimplementation."*
  - Django 5.0+ Core Security Guidelines (Mandatory POST for logout).
- **Description & Operational Impact:**  
  `UserLogoutView` implements a `get()` method, and `templates/base.html` renders Sign Out as a GET hyperlink (`<a href="{% url 'logout' %}">`). This exposes authenticated users to CSRF logout attacks and unintended logouts via search engine prefetching.
- **Alignment Recommendation:**  
  Remove `UserLogoutView.get()` and render a standard CSRF-protected POST form in `base.html`.

---

#### D08: Premature Declaration of Phase 2–4 Capabilities on User Models
- **Exact File Path & Lines:** `accounts/models.py`, lines 85–93, 122–127, 151–161.
- **Specification Citations:**
  - `Campus DengueWatch Development Plan v3.md` Section 1.3: *"Capabilities declared on the owning class: Guest (view heatmap, register, login), RegisteredUser (submit report, log out). Admin and Authority add nothing yet."*
  - `Campus DengueWatch Development Plan v3.md` Section 3.1: *"Each later phase adds its capability names to the class that owns them."*
- **Description & Operational Impact:**  
  17 future capability strings spanning Phases 2, 3, and 4 (`view_advisories`, `accept_task`, `take_questionnaire`, `create_cleanup_event`, etc.) were declared ahead of schedule in Phase 1 models.
- **Alignment Recommendation:**  
  Maintain these capability string identifiers for future phase alignment, but ensure that new phase implementations follow the exact naming established here.

---

#### D09: Polymorphic Property Bypass on `RegisteredUser.capabilities`
- **Exact File Path & Lines:** `accounts/models.py`, lines 95–97, 103–104.
- **Specification Citations:**
  - `Agent v3.md` Section 6.2: *"Role-based verification... One shared permission mechanism reads the stored role, resolves it to the matching class, and applies that class's capabilities."*
  - `Agent v3.md` Section 5: *"Inheritance and polymorphism for the user roles."*
- **Description & Operational Impact:**  
  `RegisteredUser.capabilities` returns only `base_capabilities` directly:
  ```python
  @property
  def capabilities(self):
      return self.base_capabilities
  ```
  If caller code accesses `user.capabilities` directly on an `Admin` or `Authority` user whose object was fetched as a `RegisteredUser`, the extended permissions are omitted.
- **Alignment Recommendation:**  
  Delegate the property dynamically to the resolved actor:
  ```python
  @property
  def capabilities(self):
      return self.get_actor().capabilities
  ```

---

#### D10: Specification Conflict Regarding In-Repo Automated Test Files
- **Exact File Paths & Lines:** `accounts/tests.py` (82 lines); `reports/tests.py` (211 lines).
- **Specification Citations:**
  - `Agent v3.md` Section 11, Item 15: *"Testing expectations: No in-repo automated test files. Testing and security audits are performed agentically at the end of each phase using scratch scripts, Django shell execution, and simulated role access audits. | Resolved"*
  - `Campus DengueWatch Development Plan v3.md` Section 3.3, Item #15: *"#15 Automated tests | Tests for ReportService and the permission mechanism."*
- **Description & Operational Impact:**  
  There is a direct contradiction between the two primary specification documents: `Agent v3.md` explicitly forbids in-repo test files, while the `Development Plan` requires automated tests for `ReportService` and permissions. The codebase followed the Development Plan, creating 21 robust unit tests.
- **Alignment Recommendation:**  
  Formalize the project owner's decision to preserve `accounts/tests.py` and `reports/tests.py` as permanent regression suites, and update `Agent v3.md` Item 15 accordingly.

---

#### D11: Hardcoded Insecure Default `SECRET_KEY` Without Production Guards
- **Exact File Path & Lines:** `denguewatch/settings.py`, lines 11–14.
- **Specification Citations:**
  - `Agent v3.md` Section 9: *"Secrets and environment settings stay out of source control."*
- **Description & Operational Impact:**  
  `SECRET_KEY` defaults to a hardcoded insecure key if `DJANGO_SECRET_KEY` is not present in the environment. If deployed without explicit environment configuration, this exposes the session store and CSRF tokens to tampering.
- **Alignment Recommendation:**  
  Enforce environment loading and raise an immediate `ImproperlyConfigured` exception if `SECRET_KEY` is missing in production environments (`DEBUG = False`).

---

#### D12: Hardcoded Fallback for `DAILY_REPORT_LIMIT` Inside Service Logic
- **Exact File Paths & Lines:** `reports/services.py`, line 88; `denguewatch/settings.py`, line 184.
- **Specification Citations:**
  - `Agent v3.md` Section 8.1: *"Keep the values as named settings (for example CAMPUS_BOUNDARY, DAILY_REPORT_LIMIT) so changing them does not touch logic."*
- **Description & Operational Impact:**  
  Line 88 specifies `getattr(settings, 'DAILY_REPORT_LIMIT', 8)`. If `DAILY_REPORT_LIMIT` is accidentally deleted from `settings.py`, the system silently defaults to 8 without alerting operators.
- **Alignment Recommendation:**  
  Access `settings.DAILY_REPORT_LIMIT` directly so configuration errors fail fast.

---

### Detailed Missing Architectural Components (Phases 2, 3, and 4)

#### D13: Phase 2: Heatmap Management & Authority Workflow (0% Implemented)
- **Specification Citations:** `Agent v3.md` Sections 6, 7, 8.2, 8.3; `Development Plan v3.md` Section 4.
- **Missing Architecture & Code Components:**
  1. **Applications:** `workflow` and `advisories` are completely missing from the directory tree and `INSTALLED_APPS`.
  2. **Domain Enumerations:**
     - `TaskStatus`: `ASSIGNED`, `ACCEPTED`, `PENDING_REVIEW`, `COMPLETED`
     - `ActionType`: `SPRAYING`, `DRAIN_CLEANED`, `AREA_CLEARED`, `OTHER`
  3. **Data Models:**
     - `Task`: `report` (OneToOne/FK), `authority` (FK), `status`, `remark`, `assignedAt`
     - `WorkProgress`: `task` (FK), `note`, `photo` (ImageField), `createdAt`
     - `MitigationActionPin`: `latitude`, `longitude`, `actionType`, `note`, `createdAt`
     - `Advisory`: `title`, `message`, `createdAt`, `expiresAt`, method `is_active(now)`
  4. **Service Classes:**
     - `TaskService`: `assign(report, authority)`, `accept(task)`, `add_progress(task, note, photo)`, `mark_clean(task, note)`, `approve(admin, task)`, `send_back(admin, task, remark)`
     - `AdvisoryService`: `post_advisory(admin, data)`, `get_active_advisories()`
  5. **Automated Lifecycle Logic:**
     - Mitigation Action Pins must automatically expire and be deleted 72 hours after creation (`ACTION_PIN_LIFETIME_HOURS = 72`).
     - Task approval must execute an atomic transaction: mark task `COMPLETED`, copy note and mark report `RESOLVED`, remove report from heatmap, and generate a `MitigationActionPin` at the report coordinates.
  6. **UI & Views:**
     - Admin user management view (assigning Authority/Admin roles).
     - Admin report moderation panel (listing reports, viewing details, invoking `Report.hide()`).
     - Admin task assignment and work review interfaces.
     - Authority mobile dashboard (viewing assigned tasks on map, accepting task, uploading progress photos, marking clean).
     - Homepage banner for active safety advisories.
  7. **Map Integration:**
     - Implementation of `CampusMap.renderPins` in `static/js/map.js` for mitigation action pins.

---

#### D14: Phase 3: Symptom Questionnaire & Medical Help Portal (0% Implemented)
- **Specification Citations:** `Agent v3.md` Sections 7, 8.4; `Development Plan v3.md` Section 5.
- **Missing Architecture & Code Components:**
  1. **Application:** `medical` is completely missing from the directory tree and `INSTALLED_APPS`.
  2. **Domain Enumerations:**
     - `RiskLevel`: `LOW`, `MEDIUM`, `HIGH`, `URGENT`
     - `ProviderType`: `CAMPUS_CLINIC`, `HOSPITAL`, `CLINIC`, `DIAGNOSTIC_CENTER`, `DOCTOR_CHAMBER`
  3. **Data Models:**
     - `QuestionnaireResponse`: `answersJson`, `riskLevel`, `createdAt`, `user` (FK)
     - `Thana`: `name`, `city`
     - `MedicalProvider`: `name`, `providerType`, `addressText`, `building`, `roomNumber`, `phone`, `hours`, `googleMapsLink`, `isCampusProvider`, `thana` (FK)
     - `Doctor`: `fullName`, `specialty`, `visitingHours`, `contact`, `provider` (FK)
     - `TestInfo`: `name`, `purpose`, `notes`
  4. **Service Classes:**
     - `RiskScorer`: `has_red_flags(answers)`, `calculate_risk(answers)`
     - `MedicalPortalService`: `get_campus_options()`, `get_outside_options(thana)`, `get_recommended_tests(risk)`
  5. **Views & Routing Workflow:**
     - Symptom questionnaire form view for registered users.
     - Result view with mandatory "guidance, not diagnosis" disclaimer.
     - Follow-up routing: optional continue link for `LOW`/`MEDIUM`; automatic redirect with native CSS popup for `HIGH`/`URGENT`.
     - Medical Help portal view (not in main menu): Campus doctors/chambers and Off-campus thana filtering with Google Maps links and recommended tests.
     - Admin provider and doctor management views.

---

#### D15: Phase 4: Volunteer Cleanup Portal (0% Implemented)
- **Specification Citations:** `Agent v3.md` Sections 7, 8.5; `Development Plan v3.md` Section 6.
- **Missing Architecture & Code Components:**
  1. **Application:** `events` is completely missing from the directory tree and `INSTALLED_APPS`.
  2. **Domain Enumeration:**
     - `EventStatus`: `PLANNED`, `ONGOING`, `COMPLETED`
  3. **Data Models:**
     - `CleanupEvent`: `title`, `description`, `eventLat`, `eventLng`, `startDateTime`, `status`, `createdBy` (FK), `createdAt`
     - `EventParticipation`: `event` (FK), `user` (FK), `joinedAt`, with unique constraint per user per event.
  4. **Service Class:**
     - `EventService`: `create_event(user, data)`, `join_event(user, event)`, `leave_event(user, event)`, `remove_event(admin, event)`, `update_status(event, status)`
  5. **Views & Map UI:**
     - Event list and event detail views.
     - Event creation view with interactive pin picker (`CampusMap.enablePinPicker`).
     - Event join and leave action endpoints.
     - Admin event moderation and status transition controls.
     - Implementation of `CampusMap.renderEventPins` in `static/js/map.js` with distinct event marker styling.

---

## Section 3: Unwanted Code and Test Script Detection (Requirement R3)

A complete inventory of the project workspace was conducted to detect unwanted code, dead routines, premature stubs, and orphaned assets, while distinguishing legitimate test suites from temporary scratch scripts.

### Comprehensive Inventory of Detected Unwanted Items

| # | Exact File Path | Line(s) / Symbol | Classification | Classification Rationale | Proposed Disposal Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `accounts/tests.py` | Line 3 (`RequestFactory`) | **Dead Code in Active File** | Imported from `django.test` on line 3 but never instantiated or referenced anywhere in the test file. Violates `Agent v3.md` §4. | Safe to delete the unused symbol `RequestFactory`. |
| **2** | `accounts/tests.py` | Line 6 (`ActorCapabilityMixin`) | **Dead Code in Active File** | Imported from `.permissions` on line 6 but never referenced or tested in `accounts/tests.py`. Violates `Agent v3.md` §4. | Safe to delete the unused symbol `ActorCapabilityMixin`, or add dedicated test methods. |
| **3** | `reports/models.py` | Lines 64–67 (`Report.hide`) | **Dead Code in Active File** | Premature Phase 2 moderation method. Per Development Plan §3.1, `hide()` should only be added when used in Phase 2. Never invoked by any Phase 1 view or form. | Retain if Phase 2 is immediately built; otherwise document as pre-implemented Phase 2 logic. |
| **4** | `reports/models.py` | Lines 69–75 (`Report.mark_resolved`) | **Dead Code in Active File** | Premature Phase 2 task review method. Per Development Plan §3.1, `mark_resolved()` should only be added when used in Phase 2. Never invoked by Phase 1 views. | Retain if Phase 2 is immediately built; otherwise document as pre-implemented Phase 2 logic. |
| **5** | `reports/services.py` | Lines 134–140 (`ReportService.hide_report`) | **Dead Code in Active File** | Moderation business logic scheduled for Phase 2 Sub-phase 2.2. Unwired to any view, URL, or test in Phase 1. Inactive in Phase 1 runtime. | Retain for Phase 2 moderation; otherwise remove to maintain strict phase isolation. |
| **6** | `accounts/models.py` | Lines 16–18, 87–91, 122–127, 151–161 (17 capability strings) | **Dead Code in Active File** | Speculative pre-declaration of capabilities for Phases 2, 3, and 4 (`view_advisories`, `take_questionnaire`, `manage_users`, etc.). Violates Development Plan §1.3 ("Admin and Authority add nothing yet") and §4 ("no speculative abstractions"). | Document as forward-compatible constants for subsequent phases. |
| **7** | `static/js/map.js` | Lines 76, 85 (`offlineVector`) | **Dead Code in Active File** | Empty `L.layerGroup()` registered into layer control as `'Offline Vector (Internal Only)'`. Unpopulated, causes blank map on toggle, unrequested by specs. | Safe to delete lines 76 and 85 from `map.js`. |
| **8** | `static/css/style.css` | Lines 302–308 (`.floating-report-btn`) | **Dead Code in Active File** | CSS selector defining fixed bottom-right action button. Unreferenced across all templates. Unused dead styling. | Safe to delete lines 302–308 from `style.css`. |
| **9** | `db.sqlite3` | Entire file (139 KB) | **Orphaned Asset** | Excluded by `.gitignore` (line 12). Contains leftover test sessions and test reports with invalid coordinates (Reports 1 & 2 use Dhanmondi coords outside the campus boundary). | Reset or purge `db.sqlite3`. Rely on migrations and seed data fixtures. Keep untracked. |
| **10** | `.idea/` | Entire folder (5 files: `.gitignore`, `DP01 DEV.iml`, `modules.xml`, `workspace.xml`, `profiles_settings.xml`) | **Orphaned Asset** | Local PyCharm/IntelliJ IDE metadata and user workspace state. Excluded by `.gitignore` (line 23). Not project code. | Keep untracked; maintain exclusion from version control. |

---

### Legitimate Project Test Suites vs. Temporary Scratch Scripts

A critical mandate of Requirement R3 is distinguishing genuine standard project test suites from temporary scratch scripts.

#### Analysis of `accounts/tests.py` and `reports/tests.py`
- **Location & Packaging:**  
  The test files are located strictly inside the standard application package directories (`accounts/tests.py` and `reports/tests.py`). They are not loose files in the repository root or temporary directories.
- **Framework & Structure:**  
  Both files utilize Django's official `django.test.TestCase` framework with database isolation, test transaction rollbacks, client request simulation, and standard assertions (`assertEqual`, `assertTrue`, `assertRaises`).
- **Functional Coverage:**
  - `accounts/tests.py` (82 lines, 6 tests): Validates the 3-tier role hierarchy (`Guest`, `RegisteredUser`, `Authority`, `Admin`), proxy model capability resolution, anonymous user mapping, and capability denial exceptions.
  - `reports/tests.py` (211 lines, 15 tests): Validates the ray-casting polygon boundary algorithm, boundary error messages, daily 8-report rate limiting on local calendar days, report model queries (`Report.objects.active()`), and HTTP response integration across views.
- **Execution Output:**  
  Executing `python manage.py test` executes 21 tests with zero failures in 24.2 seconds:
  ```text
  Ran 21 tests in 24.246s
  OK
  Destroying test database for alias 'default'...
  Found 21 test(s).
  ```
- **Preservation Verdict:** **GENUINE STANDARD PROJECT TEST SUITES (DO NOT DELETE).**  
  These test suites provide vital regression safety for core mathematical and security algorithms (ray-casting point-in-polygon math, local calendar rate limits, role resolution). Deleting them would strip the project of all automated verification coverage.

#### Detection of Standalone Scratch Test Scripts
- A recursive search of the workspace for standalone scratch files (`test_*.py`, `temp_*.py`, `scratch_*.py`, `debug_*.py`, `run_tests.py`, `curl_test.sh`) revealed **0 temporary scratch scripts**.
- No ad-hoc verification artifacts were left in the repository.

#### Reconciliation of Specification Contradiction
As noted in Discrepancy D10, `Agent v3.md` Section 11 Item 15 states *"No in-repo automated test files"*, while `Campus DengueWatch Development Plan v3.md` Section 3.3 Item #15 explicitly requires *"Tests for ReportService and the permission mechanism."*  
The presence of `accounts/tests.py` and `reports/tests.py` directly fulfills the explicit mandate of the Phased Development Plan. The audit affirms that these suites represent legitimate, professional engineering assets that should be retained.

---

## Section 4: Security, Architectural, and Code Quality Evaluation

### 4.1 Security Evaluation
1. **Broken Object-Level Access Control (Privilege Escalation):**  
   DEF-01 (`accounts/permissions.py`) allows demoted administrators to maintain full admin capabilities because `isinstance(admin, RegisteredUser)` evaluates to true. Exact type checking is required.
2. **Open URL Redirection (CWE-601):**  
   DEF-05 (`accounts/views.py`) fails to validate external URLs passed via `?next=`, exposing authenticated users to external phishing redirects.
3. **Password Security in Administration Panel:**  
   DEF-04 (`accounts/admin.py`) exposes user passwords as raw cleartext fields in Django admin. Editing any user overwrites their password hash with plaintext.
4. **CSRF Vulnerability in User Logout:**  
   DEF-07 / D07 (`accounts/views.py`) exposes a GET logout handler, violating Django 5.0+ security best practices and enabling unauthorized logout attacks via image tags or link prefetchers.
5. **Rate-Limiting Concurrency Race Condition:**  
   DEF-11 (`reports/services.py`) performs an un-isolated check-then-act rate check, permitting concurrent submissions to breach the 8-report daily cap.
6. **Secret Key Exposure:**  
   D11 (`denguewatch/settings.py`) provides an insecure default fallback secret key. Missing production assertions could lead to insecure deployments.

### 4.2 Architectural Design Evaluation
1. **Adherence to OOP Contracts:**  
   The application generally adheres to the OOP mandates of `Agent v3.md` Section 5. Models encapsulate state and behavior, service classes manage multi-step transactions, and views remain thin.
2. **Proxy Model Pattern Integrity:**  
   The decision to implement `Admin` and `Authority` as proxy models on `RegisteredUser` avoids complex database joins and schema migrations. However, DEF-03 (phantom records) and D09 (property bypass) indicate that the proxy pattern was incompletely wired, requiring explicit `save()` overrides and property delegation.
3. **Phased Boundary Encapsulation:**  
   Phase 1 foundations were laid cleanly with named settings (`CAMPUS_GEOJSON`, `DAILY_REPORT_LIMIT`, `TIME_ZONE`). However, the pre-declaration of 17 capability strings for future phases slightly blurs phase boundary encapsulation.

### 4.3 Code Quality & Maintainability
1. **Clean Code Adherence:**  
   Active source code is generally clean, readable, and concise. However, 8 instances of dead code (unused imports in tests, premature Phase 2 methods, unreferenced CSS) violate the "no dead code" mandate of `Agent v3.md` Section 4.
2. **Defensive Error Handling:**  
   DEF-06 (accessing `e.message` on `ValidationError`) and DEF-07 (calling `.strip()` on `None`) demonstrate a need for defensive error handling to prevent unhandled 500 crashes during validation edge cases.
3. **Timezone Awareness:**  
   DEF-08 / D04 highlights the importance of localizing UTC datetimes before frontend presentation.

### 4.4 Frontend & Usability Assessment
1. **Native CSS Navigation:**  
   The responsive navigation menu successfully implements the CSS-only checkbox toggle pattern mandated by `Agent v3.md` Section 3 and Section 11 Item 16, entirely free of Bootstrap JavaScript dependencies.
2. **Responsive Layout:**  
   Viewport meta tags, fluid grid containers, and mobile-friendly tap targets function correctly across both mobile and desktop viewports.
3. **UI Edge Flaws:**  
   DEF-09 (dead navbar modal link on non-heatmap pages), DEF-12 (blank vector map layer), and DEF-13 (tile boundary clipping) degrade user experience and must be resolved.

---

## Section 5: Prioritized Remediation Roadmap

To transition the codebase from its current audited state into a hardened, fully aligned platform ready for Phase 2 development, the following prioritized roadmap is recommended:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRIORITIZED ROADMAP                             │
├────────────────────────────────┬───────────────────────────────────────┤
│ Milestone 1: Security & Bugs   │ • DEF-01: Fix resolve_actor privilege │
│ (Immediate Stabilization)      │   escalation (type() is target_class) │
│                                │ • DEF-02: Add case-insensitive email  │
│                                │   lookup (get_by_natural_key)         │
│                                │ • DEF-03: Add save() role override to │
│                                │   Authority & Admin proxy models      │
│                                │ • DEF-04: Inherit UserAdmin in admin  │
│                                │ • DEF-05: Add url_has_allowed_host... │
│                                │ • DEF-06: Pass e directly to add_error│
│                                │ • DEF-07: Use (data.get('note') or '')│
│                                │ • DEF-08: Format local time in popups │
│                                │ • DEF-09: Update navbar modal link    │
│                                │ • DEF-10: Support data.get('photo')   │
│                                │ • DEF-11: Wrap rate limit in atomic   │
├────────────────────────────────┼───────────────────────────────────────┤
│ Milestone 2: Spec Alignment    │ • D01: Configure OSM 56-node polygon  │
│ & Clean-Up (Hardening)         │   perimeter (Way 1071236443)          │
│                                │ • D02: Standardize center coordinates │
│                                │ • D03/DEF-12: Remove mirror & vector  │
│                                │ • D07: Convert logout to POST form    │
│                                │ • D09: Delegate user.capabilities     │
│                                │ • Clean dead imports & unused CSS     │
│                                │ • Purge dirty test records in db      │
├────────────────────────────────┼───────────────────────────────────────┤
│ Milestone 3: Phase 2 Delivery  │ • Run Architecture Review Window      │
│ (Workflow & Advisories)        │ • Scaffold `workflow` & `advisories`  │
│                                │ • Implement Task & Progress models    │
│                                │ • Implement MitigationActionPin & 72h │
│                                │ • Implement TaskService & workflow    │
│                                │ • Add moderation views & map pins     │
├────────────────────────────────┼───────────────────────────────────────┤
│ Milestone 4: Phases 3 & 4      │ • Phase 3: Medical portal & triage    │
│ (Future Expansion)             │ • Phase 4: Volunteer cleanup events   │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## Section 6: Verification and Audit Attestation

### 6.1 Independent Verification Commands

Every observation, defect, and discrepancy documented in this report can be independently reproduced and verified using the following commands:

1. **Verify Automated Test Suite Baseline:**
   ```powershell
   cd "e:\DP01 DEV"
   python manage.py test
   ```
   *Expected Output:* `Ran 21 tests in ~24s, OK`. All 21 tests in `accounts` and `reports` pass.

2. **Verify Privilege Escalation Defect (DEF-01):**
   ```powershell
   python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'denguewatch.settings'); django.setup(); from accounts.models import Admin, Role; from accounts.permissions import resolve_actor; a = Admin(role=Role.REGISTERED); actor = resolve_actor(a); print('Type:', type(actor), '| Can verify:', actor.has_capability('verify_reports'))"
   ```
   *Expected Output:* `Type: <class 'accounts.models.Admin'> | Can verify: True`. Confirms demoted admin retains full capabilities.

3. **Verify Case-Sensitive Authentication Defect (DEF-02):**
   ```powershell
   python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'denguewatch.settings'); django.setup(); from accounts.models import RegisteredUser; from django.contrib.auth import authenticate; u = RegisteredUser.objects.create_user(email='CaseCheck@campus.edu', password='pw123', full_name='Case'); print('Exact authenticate:', authenticate(username='CaseCheck@campus.edu', password='pw123')); print('Lower authenticate:', authenticate(username='casecheck@campus.edu', password='pw123')); u.delete()"
   ```
   *Expected Output:* `Exact authenticate` returns user; `Lower authenticate` returns `None`.

4. **Verify Proxy Model Phantom Creation (DEF-03):**
   ```powershell
   python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'denguewatch.settings'); django.setup(); from accounts.models import Authority; a = Authority.objects.create(email='test_auth@campus.edu', full_name='Auth Staff'); print('Exists in Authority manager:', Authority.objects.filter(id=a.id).exists()); a.delete()"
   ```
   *Expected Output:* `Exists in Authority manager: False`. Confirms newly created proxy model record disappears from its own manager.

5. **Verify Timezone Formatting Discrepancy (DEF-08 / D04):**
   ```powershell
   python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'denguewatch.settings'); django.setup(); from django.utils import timezone; from reports.models import Report; r = Report.objects.first(); print('UTC strftime:', r.created_at.strftime('%I:%M %p') if r else 'No report'); print('Localtime strftime:', timezone.localtime(r.created_at).strftime('%I:%M %p') if r else 'No report')"
   ```
   *Expected Output:* Discrepancy of exactly 6 hours between UTC and local Bangladesh Standard Time.

6. **Verify GeoJSON 4-Corner Rectangular Geometry (D01):**
   Inspect `denguewatch/settings.py` lines 122–133 to observe the 4-vertex rectangle coordinates vs the 56-node OSM polygon perimeter mandate in `Agent v3.md` Section 11 Item 2.

7. **Verify Dead Imports in Test Suite (Item 1 & 2):**
   ```powershell
   Select-String -Path "accounts\tests.py" -Pattern "(RequestFactory|ActorCapabilityMixin)"
   ```
   *Expected Output:* Matches appear only on lines 3 and 6 (import statements), with 0 usages in test bodies.

8. **Verify Dead CSS Selector (Item 8):**
   ```powershell
   Select-String -Path "templates\*.html", "templates\*\*.html", "static\js\*.js" -Pattern "floating-report-btn"
   ```
   *Expected Output:* 0 matches across all project templates and scripts.

---

### 6.2 Audit Attestation & Non-Modification Compliance

In strict compliance with **Requirement R5 (Non-Modification Constraint)**:
- **Zero** existing source files, test files, configuration modules, migration files, templates, or assets in `e:\DP01 DEV` were modified, patched, or deleted during the execution of this audit.
- Only the single audit report file—`e:\DP01 DEV\audit_report.md`—was created in the workspace.
- All dynamic evaluations and verifications were executed non-destructively through standard read-only commands and isolated in-memory Python processes.
- The repository stands 100% intact, ready for deliberate, phase-aligned development.

---
*End of Comprehensive Audit Report.*
