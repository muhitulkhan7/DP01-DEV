# Agent.md: Campus DengueWatch (Campus Dengue Guard)

This file is the standing instruction set for every AI agent working on this repository.
Read it fully before writing any code. If anything here conflicts with your own judgment, this file wins.

---

## 1. Project Summary

A campus-focused dengue prevention web app that supports awareness, reporting and early guidance.

Four feature areas:

1. **Crowd-sourced mosquito activity reporting**: map pin, category, optional note and optional photo.
2. **Heatmap of hotspots**: real-time campus risk awareness, admin moderation, mitigation action pins, and authority/cleaning-staff task workflow managed by admin.
3. **Symptom questionnaire and Medical Help portal**: risk guidance only, **not diagnosis**.
4. **Volunteer cleanup portal**: student-created cleanup events, other users opt in.

Source of truth, in priority order:

1. This `Agent.md`
2. `Campus_Dengue_Guard_System_Design.txt` (design document)
3. `Development_Diagrams_drawio.pdf` (use case, activity, class, SSD 1, SSD 2, SSD 3A, SSD 3B)

If the sources disagree with each other, **stop and ask** (see Section 2).

---

## 2. Agent Behavior Rules (Non-Negotiable)

1. **Ask before any important decision** about system design or architecture. Do not assume.
2. **Do not invent features.** Implement only what is in the design document, diagrams, or the current phase's task. No extras, no "nice-to-haves", no bonus endpoints, no speculative fields.
3. **Do not invent phases.** Development phases are defined by the project owner. Work only on the phase you are told to work on. Do not start the next one.
4. **Do not invent values.** The campus boundary coordinates are supplied by the owner before the Reporting phase. The daily report rate limit is fixed **during** the Reporting phase. Until then, do not hard-code guesses. Ask.
5. **Do not rewrite finished work.** A new phase builds on the previous one (see Section 10).
6. If a requirement is ambiguous, ask **one clear question at a time**, with your proposed default, and wait for the answer.
7. When you finish a task, summarize what you changed and list any open questions. Do not silently expand scope.
8. **Before starting any phase or sub-phase, run the architecture review window** (Section 10.1). Do not write code until it is done.

### What counts as an "important decision" (always ask)

- Adding or changing a model, field, relation or enum not in the class diagram
- Adding a Python package or JS library
- Changing folder or app structure
- Changing the role or permission model
- Any behavior the design doc or diagrams do not specify

### What does not need asking

- Naming a local variable
- Formatting, docstrings, template markup
- Implementing something exactly as the diagrams specify

---

## 3. Technical Stack (Fixed)

| Layer    | Choice                                           |
|----------|--------------------------------------------------|
| Backend  | Python, Django                                   |
| Database | SQLite                                           |
| Frontend | Django templates + Bootstrap                     |
| Maps     | Leaflet.js + OpenStreetMap tiles                 |

Do not introduce DRF, React, HTMX, Celery, PostgreSQL or any other stack component without asking.

### JavaScript rule

**As little JS as possible, only for the map portion** (Leaflet map, click-to-drop-pin, markers, heatmap layer).
Everything else (forms, navigation, validation, moderation, filtering) is server-side Django.
Any JS that is not map-related is a violation.

### Device support rule (key criteria): PC and mobile

The app is used from **both PC and mobile phones**. Every page must be designed and tested for both. This is a requirement of every phase, not a later polish step.

- **Responsive, mobile-first.** Build with Bootstrap's grid and responsive utilities. Do not create separate mobile and desktop templates or a separate mobile site. One template serves both.
- **Viewport meta tag** (`width=device-width, initial-scale=1`) is set once in the base template.
- **Layout:** content stacks in a single column on phones and uses multi-column layouts on larger screens. The menu collapses into a toggle menu on small screens and shows in full on larger screens (see the menu rule below).
- **Navigation menu (native CSS, current decision):** the menu used on mobile and PC is styled and toggled with **native CSS only** (for example a checkbox/label toggle or `<details>`, with media queries). It must not depend on JavaScript, including Bootstrap's JS collapse component. Bootstrap's JS bundle is not needed for the menu and is not to be added unless the owner asks. **This is a current decision and may change during implementation.** If native CSS proves insufficient, stop and ask; do not switch approaches on your own.
- **Touch-friendly:** buttons, links and form controls are large enough to tap comfortably (Bootstrap defaults or larger). No hover-only interactions. Everything must work by tap.
- **Map (Leaflet):**
  - The map container has an explicit responsive height (for example a viewport-relative height) so it is usable on a phone and does not trap page scrolling.
  - Dropping a pin works by **tap** as well as click, and the pin's coordinates auto-fill on both.
  - Zoom and pan work with touch gestures. Markers and popups are readable and tappable on small screens.
  - Map legends and controls must not cover the map on small screens.
- **Forms:** use correct input types, such as `tel`, `email`, `datetime-local`, and `number`, so mobile keyboards and pickers are appropriate. Photo upload should let a phone user choose from the gallery or the camera.
- **Tables and lists** (admin review panel, task lists, provider lists) must not overflow the screen. Use responsive table wrappers or card/list layouts on small screens.
- **Images** (report and progress photos) scale to their container and never cause horizontal scrolling.
- **No horizontal scrolling** on any page at phone widths.
- Responsiveness is achieved with Bootstrap classes and CSS. **Do not add JavaScript for layout or responsiveness.** The JS-only-for-map rule still applies.
- Verify each page at a typical phone width and a desktop width before a phase is considered done.

---

## 4. Code Quality Rules

- Backend code must be **clean, simple, and easy to read and follow**.
- **No extra lines of code beyond what is necessary.** No dead code, no unused imports, no commented-out code, no speculative abstractions, no over-commenting.
- Prefer Django built-ins (generic views, ModelForms, `login_required`, the auth system, the ORM) over custom reimplementation.
- Short methods with one responsibility. Clear names. Docstrings only where the intent is not obvious.
- Business rules live in **service classes or model methods**, never in templates and never duplicated in views.
- Views stay thin: parse the request, call a service or model method, return a response.

---

## 5. OOP Rules

**Use OOP wherever it can reasonably be used.** Concretely:

- **Models** carry their own behavior (e.g. `Report.hide()`, `Report.mark_resolved(note)`, `Advisory.is_active(now)`).
- **Service classes** hold multi-step business logic (see Section 8).
- **Class-based views** are the default. Share behavior through mixins (for example the shared permission mixin from Section 6.2).
- **Inheritance and polymorphism** for the user roles (Section 6).
- **Enumerations** use `models.TextChoices`, one class per enum in the class diagram.
- Use encapsulation: callers use the public methods defined in the class diagram, not raw field manipulation.
- Do not create a class where a plain function is clearly simpler and nothing is gained from OOP.

---

## 6. User Classes and Role-Based Access

### 6.1 Hierarchy

```
Guest                        (separate class, NOT a database model)

RegisteredUser               (parent, Django user model with a stored `role` field)
 ├── Admin                   (proxy model, sibling of Authority)
 └── Authority               (proxy model, sibling of Admin)
```

- **Guest is a separate class.** It is not a parent of RegisteredUser and is not stored in the database. It represents an unauthenticated visitor with limited access.
- **RegisteredUser is the parent class.** Admin and Authority are its two child classes and are **siblings**. Neither inherits from the other.
- **Implementation (confirmed by owner):** proxy models on **one user table** with a `role` field. No multi-table inheritance, no separate Admin/Authority tables.
  - `RegisteredUser` is the custom user model (extends Django's `AbstractUser` or `AbstractBaseUser`; **ask** which before building).
  - `Admin` and `Authority` are `proxy = True` subclasses with a custom manager that filters by `role`.
  - Child classes add their own methods and capabilities; they must not duplicate parent behavior.
- Fields per the class diagram: `id`, `fullName`, `email`, `passwordHash`, `dateJoined`, plus the stored `role` (see Section 13). Use Django's password hashing. Never store plain passwords.

### 6.2 Role-based verification (confirmed by owner)

Authority-level verification uses **subclass proxies**. Three parts work together:

1. **The role is kept in the database** on the user record. It is the single source of truth for who someone is.
2. **Role-specific capabilities are defined on the sibling proxy classes.** `RegisteredUser` declares what a registered user can do. `Admin` and `Authority` each add only their own capabilities on top of the inherited ones. `Guest` declares its own small set. A capability is declared once, on the class that owns it, and never repeated elsewhere.
3. **One shared permission mechanism** reads the stored role, resolves it to the matching class, and applies that class's capabilities. Views and services use this single mechanism (for example one reusable mixin plus one check used by the service classes). There is no second permission path.

Rules:

- Do not scatter `if user.role == ...` checks across views, templates or services. The role value is read in one place only: the shared mechanism.
- Do not use a numeric rank or "minimum role" ordering. Admin and Authority are siblings, so Admin does **not** gain Authority actions (accept task, upload progress, mark area clean), and Authority does not gain Admin actions.
- Anonymous visitors are resolved to a `Guest` instance by the same mechanism, so every request has an actor with capabilities.
- Service methods that need a privileged actor verify the actor through the same mechanism.
- The exact code shape (for example a `capabilities` set on each class and a role-to-class registry) must stay as small and simple as possible. If more than this is needed, ask first.

The informal ordering from the design doc, `Guest < Registered User < Authority < Admin`, describes how much each class can do. It is **not** an inheritance chain and is not how access is enforced.

### 6.3 Capabilities per role

**Guest** (no login)
- View heatmap and reported areas
- View advisories
- View mitigation action pins
- View cleanup events (shown on map)
- Register, log in

**Registered User** (everything a Guest can do, plus)
- Submit report
- Create cleanup event
- Join cleanup event
- Leave cleanup event
- Take symptom questionnaire
- Access medical portal
- Log out

**Authority** (inherits Registered User, plus)
- View assigned areas
- Accept task
- Update/upload work progress (for admin review)
- Mark area clean (sends the task to admin review)

**Admin** (inherits Registered User, plus)
- Manage users
- Verify reports (hides a report)
- Assign reported location to an authority
- Review work (approve or send back with remark)
- Add / remove mitigation action pins
- Remove cleanup events
- Update event status
- Post advisories
- Manage doctor portal (add/update doctor and provider information)

Admin does **not** accept tasks or upload work progress. Those are Authority-only capabilities.

---

## 7. Domain Model (from the UML Class Diagram)

Implement exactly these classes. Do not add fields or models that are not listed here without asking.

### Enumerations (`TextChoices`)

| Enum             | Values                                                          |
|------------------|-----------------------------------------------------------------|
| `ReportStatus`   | VISIBLE, HIDDEN, RESOLVED                                       |
| `ReportCategory` | STAGNANT_WATER, MANY_MOSQUITOES, BITE_INCIDENT                  |
| `TaskStatus`     | ASSIGNED, ACCEPTED, PENDING_REVIEW, COMPLETED                   |
| `ActionType`     | SPRAYING, DRAIN_CLEANED, AREA_CLEARED, OTHER                    |
| `EventStatus`    | PLANNED, ONGOING, COMPLETED                                     |
| `RiskLevel`      | LOW, MEDIUM, HIGH, URGENT                                       |
| `ProviderType`   | CAMPUS_CLINIC, HOSPITAL, CLINIC, DIAGNOSTIC_CENTER, DOCTOR_CHAMBER |

### Models

| Model                 | Fields (per diagram)                                                                                              | Behavior |
|-----------------------|-------------------------------------------------------------------------------------------------------------------|----------|
| `Report`              | latitude, longitude, category, note, photo, createdAt, status, resolvedNote; FK to the reporting user              | `hide()`, `mark_resolved(note)` |
| `Task`                | report, authority, status, remark, assignedAt                                                                     | status transitions via `TaskService` |
| `WorkProgress`        | task, note, photo, createdAt                                                                                       | |
| `MitigationActionPin` | latitude, longitude, actionType, note, createdAt                                                                  | |
| `Advisory`            | title, message, createdAt, expiresAt                                                                              | `is_active(now)` |
| `CleanupEvent`        | title, description, eventLat, eventLng, startDateTime, status, createdBy, createdAt                               | |
| `EventParticipation`  | event, user, joinedAt                                                                                             | one row per user per event |
| `QuestionnaireResponse` | answersJson, riskLevel, createdAt; FK to user                                                                   | |
| `MedicalProvider`     | name, providerType, addressText, building, roomNumber, phone, hours, googleMapsLink, isCampusProvider; FK to Thana for off-campus | |
| `Doctor`              | fullName, specialty, visitingHours, contact; FK to MedicalProvider                                                | |
| `Thana`               | name, city                                                                                                        | |
| `TestInfo`            | name, purpose, notes                                                                                              | |

Relationships follow the class diagram: a user creates reports and events and joins events (`EventParticipation`), a task links one report to one authority, a task has many `WorkProgress` entries, a provider has doctors, and a provider is located in a thana (off-campus only).

### Service classes (business logic)

| Service                | Methods |
|------------------------|---------|
| `ReportService`        | `validate_boundary(lat, lng)`, `check_rate_limit(user)`, `create_report(user, data)`, `hide_report(admin, report)` |
| `TaskService`          | `assign(report, authority)`, `accept(task)`, `add_progress(task, note, photo)`, `mark_clean(task, note)`, `approve(admin, task)`, `send_back(admin, task, remark)` |
| `EventService`         | `create_event(user, data)`, `join_event(user, event)`, `leave_event(user, event)`, `remove_event(admin, event)`, `update_status(event, status)` |
| `AdvisoryService`      | `post_advisory(admin, data)`, `get_active_advisories()` |
| `MedicalPortalService` | `get_campus_options()`, `get_outside_options(thana)`, `get_recommended_tests(risk)` |
| `RiskScorer`           | `has_red_flags(answers)`, `calculate_risk(answers)` |

Service methods that require a privileged actor must verify the actor's role.

---

## 8. Feature Behavior Specification

### 8.1 Reporting (SSD 1, Activity Diagram)

1. Anyone can open the map and see active reports (heatmap layer). No login needed to view.
2. **Report button gate:** when a user who is not logged in clicks the Report button, a **popup** asks them to log in or register (with links to both). Only logged-in users reach the report form. The popup is built with native HTML/CSS only, no JS (JS stays map-only).
3. A logged-in user opens the report form, **clicks (or taps) the map to drop a pin**, and latitude/longitude are auto-filled.
4. The user selects a category, and optionally adds a note and a photo, then submits.
5. Server-side checks still run on submit **in this order** (the popup is a convenience, not the security check):
   1. **Logged in?** If not, redirect to the login page.
   2. **Inside campus boundary?** If not, show "Outside campus boundary".
   3. **Daily rate limit exceeded?** If so, show "Too many reports today".
6. If all checks pass, save the report, show a success message, and the new report appears on the heatmap.

Keep the values as named settings (for example `CAMPUS_BOUNDARY`, `DAILY_REPORT_LIMIT`) so changing them does not touch logic. The **campus boundary** is provided by the owner before this phase starts. The **daily rate limit** is fixed during this development phase: do not choose a number earlier, and at this phase confirm the number with the owner before coding it.

### 8.2 Heatmap and Admin Moderation (SSD 3A)

- The heatmap is real-time campus risk awareness for the public. **"Real-time" means the latest data every time the page loads or is refreshed** (confirmed by owner). Django passes the report points into the template and Leaflet draws them. No polling, no live push, no auto-refresh.
- **Only mosquito reports with status `VISIBLE` contribute to heat intensity, and all three categories (`STAGNANT_WATER`, `MANY_MOSQUITOES`, `BITE_INCIDENT`) count equally** (confirmed by owner). `HIDDEN` and `RESOLVED` reports do not count. Mitigation action pins and cleanup event pins never contribute to the heatmap in any way.
- Admin opens the report review panel, lists reports with status, and opens a report's details (location, category, note, photo).
- Admin decisions per report:
  - **Spam or invalid** → `hide` the report (`status = HIDDEN`). Hidden reports disappear from the public map.
  - **Valid, no action needed** → report stays visible as an active hotspot.
  - **Valid, action needed** → admin assigns it to an Authority (`Task` created with status `ASSIGNED`).
- **Terminology:** "mitigation action pin" (class `MitigationActionPin`) is the one name for the pin showing that action was taken. "Action pin" is only a short form of it.
- Mitigation action pins are visible to everyone. They are created in two ways: automatically on admin approval (Section 8.3), and manually by the Admin, who can also remove them.
- "Verify reports" in the design doc means hiding invalid ones. Use `hide()`; do not hard-delete reports. (The activity diagram says "Hide / Delete" while the class diagram only has `hide`. Confirm with the owner if hard delete is wanted.)

### 8.3 Authority Workflow (SSD 3B)

```
ASSIGNED ──accept──▶ ACCEPTED ──mark clean──▶ PENDING_REVIEW ──approve──▶ COMPLETED
    ▲                                                │
    └──────────── send back (with remark) ───────────┘
```

1. Authority views assigned areas (tasks shown on a map).
2. Authority accepts a task (`ACCEPTED`).
3. Authority uploads work progress (note + optional photo) as many times as needed.
4. Authority marks the area clean with a resolved note, and the task becomes `PENDING_REVIEW`. The note is saved as the **final `WorkProgress` entry** (no new field on `Task`).
5. Admin reviews progress and either:
   - **Approves (one step, confirmed by owner):** task becomes `COMPLETED`, the report becomes `RESOLVED`, the resolved note is copied to `Report.resolvedNote`, and the report's pin changes into a **mitigation action pin** at the same location. The admin picks the `ActionType` on the approve form, and the pin's note is the Authority's resolved note. There is no separate "add pin" step after approval.
   - **Sends back with a remark**: task returns to `ASSIGNED` with the remark.
6. **On admin approval only:** the report leaves the heatmap and is replaced by the mitigation action pin. Nothing changes earlier, for example when the Authority marks the area clean. The resolved report stays in the database for history but is not shown on the map. Resolved reports do not count toward hotspot intensity, and the pin never contributes to the heatmap.
7. **72-hour lifetime:** every `MitigationActionPin` is deleted automatically 72 hours after its `createdAt`. Expired pins are deleted when the map page loads (service method, **no scheduler**). The lifetime is a named setting (for example `ACTION_PIN_LIFETIME_HOURS`), not a hard-coded number.

Invalid transitions must be rejected by `TaskService`, not by the template or view.

### 8.4 Symptom Questionnaire and Medical Help Portal (SSD 2)

- The user must be logged in.
- The questionnaire is a simple symptom form.
- `RiskScorer` runs first:
  - **Red-flag symptoms** → risk `URGENT`, show emergency advice.
  - Otherwise → risk `LOW`, `MEDIUM` or `HIGH` with advice.
- Every submission is saved as a `QuestionnaireResponse`.
- This is **risk guidance, not diagnosis.** Show that disclaimer on the questionnaire and results pages.
- **The Medical Help Portal is a follow-up to the questionnaire** (confirmed by owner). It is reached from the questionnaire result, not as a standalone page in the menu. Behavior by risk level:
  - **`LOW` or `MEDIUM`**: the result page shows an **option** to continue to the Medical Help Portal.
  - **`HIGH` or `URGENT`** (same treatment, confirmed by owner): the user is taken **directly** to the Medical Help Portal, with a **popup** telling them they should follow proper medical directives. The popup is native HTML/CSS, no JS. The saved `QuestionnaireResponse` still records the exact risk level.
- The portal has two options:
  - **On campus**: show doctor details, building, room number, contact and visiting-hour guidelines.
  - **Off campus**: user picks a **thana**, then sees hospitals, clinics, and doctor chambers in that thana, with a suitable dengue doctor, location (including **Google Maps link**), contact, and visiting-hour guidelines for appointments.
- The portal also shows **tests that can be done independently** before visiting a doctor, based on risk level (`TestInfo`).
- Exact risk-scoring rules and the question list are not defined in the design doc. **Ask the owner before implementing them.**
- Admin manages doctor and provider information.

### 8.5 Volunteer Cleanup Portal

- Logged-in users create cleanup events (title, description, map location, start date/time).
- Logged-in users can join and leave events.
- Admin can remove inappropriate events and update event status.
- Event status flow: `PLANNED → ONGOING → COMPLETED`.
- Events appear on the map with **custom pins**, separate from report markers and mitigation action pins.
- Guests can view events but cannot create or join.

### 8.6 Advisories

- Admin posts advisories (title, message, expiry).
- Everyone sees active advisories (`is_active(now)`), and expired ones are hidden.

---

## 9. Suggested Code Conventions

- PEP 8. Meaningful names. Snake_case in Python (diagram camelCase maps to snake_case: `fullName` becomes `full_name`).
- One Django app per feature area is the intended direction, but **confirm the app layout with the owner at the start of the first phase** before creating apps.
- Templates extend one base template (Bootstrap) that already includes the viewport tag and the native-CSS menu. Reuse partials; do not copy-paste markup.
- Write every template mobile-first and responsive (see the device support rule in Section 3).
- Static map JS lives in a single small file per page that needs it.
- Keep all user-facing messages exactly as the diagrams word them where specified ("Outside campus boundary", "Too many reports today", and so on).
- Validate all input on the server. Use ModelForms.
- Secrets and environment settings stay out of source control.

---

## 10. Phase Transition Rules

> **Phases are defined by the project owner, not by the agent. Do not create, reorder or merge phases on your own.**
> Phase list (Approved from `Campus DengueWatch Development Plan v3.md`):
> - **Phase 1: Reporting + viewing the heatmap** (Project environment, auth and role mechanism, report submission, public heatmap)
> - **Phase 2: Heatmap management and authority workflow** (Moderation, user/role management, task workflow, mitigation action pins, advisories)
> - **Phase 3: Symptom questionnaire and Medical Help portal** (Risk scoring, portal campus/off-campus, doctor/provider management)
> - **Phase 4: Volunteer cleanup portal** (Events, join/leave, event pins on map, admin removal and status)

Every phase must make the next one easy. Follow these rules:

1. **Additive only.** A new phase adds new code. It does not rewrite, rename, or restructure code from earlier phases unless the owner approves.
2. **Inherit, do not duplicate.** Extend earlier phase code through subclassing, mixins, new service methods, or new models. Never copy-paste earlier code.
3. **Stable interfaces.** Do not change signatures of earlier public classes and methods. If a change is truly required, ask first.
4. **Additive migrations.** New phases add new migrations. Do not edit or squash earlier migrations.
5. **Self-contained phases.** Each phase leaves the project in a working, runnable state. Features not yet built must not leave broken links, dead buttons or half-wired URLs. Do not stub future features.
6. **Plug-in wiring.** A new feature should need only: its own models/services/views/templates, a URL include, and a navigation link.
7. **Phase checklist before finishing a phase:**
   - [ ] Only the requested scope was built
   - [ ] Roles and permissions enforced for every new view
   - [ ] No unused code or imports
   - [ ] JS used only for map behavior
   - [ ] New pages checked at phone width and desktop width (no horizontal scroll, tap-friendly, map usable)
   - [ ] Earlier phases still work
   - [ ] Open questions listed for the owner

### 10.1 Architecture review window (required before every phase and sub-phase)

Questions that exist now, or that appear later, are settled in a review window. They are **not** settled by the agent guessing during development. Before writing any code for a phase or sub-phase, the agent must:

1. Review the architecture for that phase: models, services, views, templates, URLs, permissions, and how it plugs into earlier phases (Section 10 rules).
2. List every open question that applies to the phase, taking them from Section 11 and from anything new the agent noticed.
3. Present the review and the questions to the owner, each with a proposed default, one question at a time.
4. Wait for the owner's answers, record any decision in this file, and only then start coding.

If a new question arises mid-phase, stop and ask. Do not carry on with an assumption. The owner may also run a review window on request at any time.

---

## 11. Open Items (Ask the Owner, Do Not Assume)

This table is the checklist for the architecture review windows in Section 10.1. Resolve each item in the window of the phase named in its last column, at the latest.

| # | Item | Needed before |
|---|------|---------------|
| 1 | Phase list and order: Resolved in `Campus DengueWatch Development Plan v3.md` (Phases 1-4) | Completed |
| 2 | Campus boundary coordinates & daily report limit: OpenStreetMap 56-node polygon perimeter for ULAB Permanent Campus (Way 1071236443, center `23°45′35.9″N 90°20′56.3″E` / `23.759973, 90.348976`) plus 1 km viewport buffer restriction; daily limit `8` reports/day per user. | Resolved |
| 3 | Custom user base class: `AbstractUser`; login identifier: `email`. | Resolved |
| 4 | What "Manage users" covers, and how Authority accounts are created (admin assigns the role, or other) | Auth/roles phase |
| 5 | Heatmap rendering: `leaflet.heat` plugin with Leaflet via CDN. | Resolved |
| 6 | Photo storage: Django `ImageField` with local media directory (`MEDIA_ROOT` / `MEDIA_URL`), using Pillow. | Resolved |
| 7 | Hide only, or hard delete for reports | Moderation phase |
| 8 | Questionnaire questions, red-flag rules, and risk-scoring thresholds | Questionnaire phase |
| 9 | Who may update event status (admin only per design doc; confirm the creator cannot) | Cleanup events phase |
| 10 | Django app layout: `accounts` and `reports` for Phase 1; one app per later feature. | Resolved |
| 11 | Admin UI: custom pages in our own templates for everything, or Django's built-in admin site for user and doctor management? | Auth/roles phase |
| 12 | Time zone: `Asia/Dhaka`, with "today" defined as the local calendar day. | Resolved |
| 13 | Reporter name on map popups: Not shown publicly. | Resolved |
| 14 | Starting data: who loads the initial thanas, providers, doctors and test info (seed fixtures or entered by admin)? | Questionnaire phase |
| 15 | Testing expectations: No in-repo automated test files. Testing and security audits are performed agentically at the end of each phase using scratch scripts, Django shell execution, and simulated role access audits. | Resolved |
| 16 | Native-CSS menu: Maintained using native CSS (no Bootstrap JS). | Resolved |

---

## 12. Out of Scope

Do not build, suggest, or scaffold: analytics or dashboards (explicitly removed from the diagrams), diagnosis features, notifications, chat, payments, public APIs, social features, native mobile apps (the web app is responsive instead), or any feature not listed above.

---

## 13. Known Differences Between Agreed Decisions and the Diagrams

The diagrams are a source of truth, but the decisions below were agreed after them. Follow the decisions. Do not edit the diagram files. Flag these to the owner so the diagrams can be updated.

1. **`role` field.** The class diagram's `RegisteredUser` has no `role` attribute. The owner decided the role is stored in the database, so `role` is added to `RegisteredUser`.
2. **Proxy classes.** The diagrams show Admin and Authority as subclasses but say nothing about proxy models or the shared permission mechanism (Section 6.2).
3. **Siblings, not a chain.** The design doc's access order reads like a linear ladder. The class diagram and owner decision make Admin and Authority siblings.
4. **User fields.** The diagram lists `fullName` and `passwordHash`. Django stores the hash in its own `password` field. Map the names; do not store a second copy.
5. **Photos.** The diagram uses `photoUrl` on `Report` and `WorkProgress`. See Open Item 6.
6. **User links.** The diagram's attribute lists do not show the user on `Report` and `QuestionnaireResponse`, but the associations and the rate-limit check (`countReportsToday(userId)`) require it. Add the user link to these models.
7. **Task notes.** The Authority's note is saved as the final `WorkProgress` entry and copied to `Report.resolvedNote` on approval. No schema change.
8. **Hide vs hard delete.** See Open Item 7.
9. **Menu approach.** Native CSS is the current decision and may change (Section 3).
10. **Login gate.** SSD 1 redirects a guest to the login page at submit. The agreed behavior is a login/register popup when a guest clicks the Report button. The server-side login check on submit stays as a backstop.
11. **Medical portal.** SSD 2 offers the portal after every risk result and the use case diagram lists "View Medical Portal" directly under Registered User. The agreed behavior: portal only as a questionnaire follow-up; optional for `LOW`/`MEDIUM`, direct redirect with a popup for `HIGH` and `URGENT`.
12. **Resolved reports and mitigation action pins.** SSD 3B step 7 has the admin add the pin as a separate step after approval, and its note says resolved status is visible on the heatmap. The agreed behavior: approval is one step that also changes the report's pin into a mitigation action pin (step 7 is removed), resolved reports leave the heatmap, pins never count toward heat, and every mitigation action pin is deleted 72 hours after creation. The class diagram has no expiry field; `createdAt` is enough. The manual Add / Remove Action Pin use case stays.
13. **Real-time heatmap.** The agreed meaning is latest data on page load or refresh, with no live updating.
