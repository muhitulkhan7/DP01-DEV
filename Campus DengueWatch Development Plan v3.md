# Campus DengueWatch: Development Plan

Built from `Agent_v3.md` and `Development_Diagrams_drawio.pdf` (use case, activity, class, SSD 1, 2, 3A, 3B). Four phases, one per key feature. Each phase is additive: it adds models, services, views, templates, a URL include and a nav link, and never rewrites earlier work.

## 1. Phase Overview

| Phase | Key feature | Delivers | Builds on |
| --- | --- | --- | --- |
| 1 | Reporting + viewing the heatmap | Project environment, auth and role mechanism, report submission, public heatmap | Nothing |
| 2 | Heatmap management and authority workflow | Moderation, user/role management, task workflow, mitigation action pins, advisories | Phase 1 |
| 3 | Symptom questionnaire and Medical Help portal | Risk scoring, portal (campus and off-campus), doctor/provider management | Phase 1 (auth, base template) |
| 4 | Volunteer cleanup portal | Events, join/leave, event pins on the map, admin removal and status | Phase 1 (auth, map) |

Phases 3 and 4 depend only on Phase 1, so they can be reordered by the owner without rework.

## 2. Rules Applied to Every Phase

- **Start with the architecture review window** (Agent.md 10.1): review models, services, views, URLs and permissions, list the open items for that phase with a proposed default each, ask one at a time, record decisions in Agent.md, then code.
- **Finish with the Section 10 checklist:** only the requested scope, permissions on every new view, no unused code, JS only for the map, checked at phone and desktop width, earlier phases still work, open questions listed.
- **Done means runnable.** No dead links, no stubbed future features. Nav links are added only when the page exists.
- Views stay thin, rules live in services and model methods, Django built-ins first, ModelForms for all input, server-side validation.
- **Mobile-first on every page.** One responsive template set, Bootstrap grid, native-CSS menu, tap-friendly controls, no horizontal scroll.

## 3. Phase 1: Reporting and Heatmap Viewing

**Goal:** a guest can open the campus heatmap. A logged-in user can drop a pin, submit a report that passes the boundary and rate-limit checks, and see it on the heatmap.

**Scope note:** Agent.md lists the heatmap as feature 2. Per the owner, Phase 1 covers *viewing* it. Moderation, tasks, pins and advisories (the rest of feature 2) are Phase 2.

### 3.1 Foundations laid now so later phases plug in

| Decision | Why it removes later work |
| --- | --- |
| Custom user model with stored `role` created **before the first migration** | Changing the user model after migrating is painful. Admin and Authority proxies and Phase 2 role management then need no schema change. |
| One shared permission mechanism (role-to-class registry, one mixin, one actor-resolving step), with `Guest` as a non-DB class | Each later phase adds its capability names to the class that owns them. No `if user.role` checks anywhere. |
| Full `Report` model per the class diagram, including `status` and `resolved_note` | Phase 2 needs no changes to the model. Only `hide()` and `mark_resolved()` are added when used. |
| `Report.objects.active()` returns `VISIBLE` only, and the heatmap uses it | Hidden and resolved reports leave the map automatically in Phase 2. No map code changes. |
| Map JS in one small file made of independent functions (`initMap`, `renderHeat`, `enablePinPicker`) reading data from `json_script` blocks | Phase 2 adds `renderPins`, Phase 4 adds `renderEventPins`. The pin picker is reused for events and manual pins. |
| Base template with viewport tag, native-CSS menu, messages area and blocks | Later phases only add a nav link and their own pages. |
| Named settings: `CAMPUS_BOUNDARY`, `DAILY_REPORT_LIMIT`, `TIME_ZONE` | Values change without touching logic. |

### 3.2 Sub-phases

**1.0 Architecture review window**

- Settle the items in 3.3 below. Nothing is coded until the owner has answered.

**1.1 Project scaffold**

- Virtual environment, `requirements.txt`, Django project, SQLite, `.gitignore`, secrets via environment settings.
- Create the apps agreed in 1.0. Proposed: `accounts`, `reports`. Later phases add `workflow`, `advisories`, `medical`, `events`.
- Static and media configuration, `TIME_ZONE`.
- Exit: `runserver` works and the first migrations run clean.

**1.2 Base template and shell**

- `base.html`: viewport tag, Bootstrap CSS (no Bootstrap JS), native-CSS toggle menu, messages partial, content blocks.
- Menu shows only links that exist: Heatmap, Login, Register, Report, Logout. Links depend on capability.
- Exit: the shell renders at phone and desktop width with a working CSS-only menu.

**1.3 Accounts and role mechanism**

- `RegisteredUser` with a `Role` TextChoices (`REGISTERED`, `ADMIN`, `AUTHORITY`), fields mapped from the diagram (`full_name`, `email`, `date_joined`, Django's own password hash).
- `Admin` and `Authority` as proxy models with role-filtered managers. `Guest` as a plain class.
- Capabilities declared on the owning class: Guest (view heatmap, register, login), RegisteredUser (submit report, log out). Admin and Authority add nothing yet.
- One mixin and one registry to resolve any request to its actor.
- Register, login and logout views using ModelForms and the Django auth system.
- Exit: users can register, log in and out. Every request has an actor.

**1.4 Report domain**

- `ReportStatus` and `ReportCategory` enums.
- `Report` model per the class diagram plus the user FK, with the `active()` queryset method.
- Additive migration.

**1.5 ReportService and form**

- `ReportService.validate_boundary`, `check_rate_limit` (the user's reports on the local calendar day), `create_report`.
- Checks run in order: logged in (view mixin), then boundary ("Outside campus boundary"), then rate limit ("Too many reports today"). Messages use the exact diagram wording.
- `ReportForm` ModelForm: category, note, photo, latitude, longitude. Input types are mobile-friendly, and the photo input accepts camera or gallery.
- Exit: the service is exercised through the Django shell or tests for all three outcomes.

**1.6 Map foundation**

- `map.html` partial with a responsive viewport-relative height that does not trap page scroll. Leaflet and OpenStreetMap tiles.
- `map.js`: `initMap`, `renderHeat`, `enablePinPicker` (tap or click drops a pin and auto-fills latitude and longitude).
- Legend sits below the map on small screens.
- Exit: the map pans, zooms and picks a pin by touch and by mouse.

**1.7 Heatmap page (home)**

- Public `HeatmapView`: passes `Report.objects.active()` as JSON, drawn by `renderHeat`. All categories count equally. Page load shows the latest data, with no polling.
- Popups show category, note and photo. The reporter's name is not shown (default for the review window).
- Report button: a logged-in user goes to the form. A guest gets a CSS-only popup (`:target`) with Login and Register links that return to the report page.
- Exit: a guest sees the map and the popup gate.

**1.8 Report page**

- `ReportCreateView`: login required plus the capability check, calls the service, shows the success message ("Show success message" in the activity diagram), and redirects to the heatmap where the new report appears.
- Failures redisplay the form with the diagram's messages.
- Exit: the full SSD 1 flow works for a user.

**1.9 Verification and hand-off**

- Walk through the activity diagram: guest gate, outside boundary, over the daily limit, success, and a report with and without a note or photo.
- Check each page at phone and desktop width. Check JS is map-only. Run the Section 10 checklist.
- Write a summary of changes and the open questions list.

### 3.3 Open items for the Phase 1 review window (Resolved)

| Agent.md item | Agreed Decision |
| --- | --- |
| #10 App layout | `accounts`, `reports` now. One app per later feature. |
| #3 User base class and login id | `AbstractUser`, email as the login identifier. |
| #2 Campus boundary & rate limit | GeoJSON polygon boundary (center ~`23°45′35″N 90°20′54″E` / `23.759791, 90.348268`), configured in `CAMPUS_BOUNDARY` setting. Daily limit: `8` reports/day. |
| #5 Heatmap rendering | `leaflet.heat` plugin for a true heat look via CDN. |
| #6 Photo storage | `ImageField` with local media (adds Pillow). |
| #12 Time zone | `Asia/Dhaka`, with "today" as the local calendar day. |
| #13 Reporter name on popups | Not shown. |
| #15 Automated tests | Tests for `ReportService` and the permission mechanism. |
| #16 Native-CSS menu | Keep native-CSS toggle menu (no Bootstrap JS). |
| New: Leaflet and Bootstrap delivery | CDN for both, CSS only for Bootstrap. |

## 4. Phase 2: Heatmap Management and Authority Workflow

**Goal:** finish feature 2. Admin moderates reports, assigns them to Authorities, and reviews their work. Approved work turns a report into a mitigation action pin. Advisories are posted by Admin and seen by everyone.

**Plugs into Phase 1:** new `workflow` and `advisories` apps; new capabilities on `Admin` and `Authority`; new layer functions in `map.js`; extra context on the heatmap view.

### Sub-phases

**2.0 Architecture review window.** Items #4 (what Manage Users covers, how Authority accounts are made), #7 (hide only or hard delete), #11 (custom admin pages or Django admin). Also: where pin expiry lives and how the Admin selects the Authority and the `ActionType`.

**2.1 Manage Users.** Admin lists users and changes roles, which is how Authority accounts come to exist. Capabilities are added on `Admin`.

**2.2 Moderation.** `Report.hide()`, `ReportService.hide_report(admin, report)`. Review panel (responsive list or cards with status) and a report detail page (location, category, note, photo). Hidden reports vanish from the heatmap through the existing `active()` queryset. No map code changes.

**2.3 Tasks and assignment.** `TaskStatus`, `Task`, `TaskService.assign`. Admin assigns a valid report to an Authority from the report detail page. The report stays visible as a hotspot.

**2.4 Authority side.** `WorkProgress`; `TaskService.accept`, `add_progress`, `mark_clean`. The Authority sees assigned areas on a map, accepts, uploads progress with an optional photo, and marks the area clean. The note is saved as the final `WorkProgress` entry and the task becomes `PENDING_REVIEW`. Invalid transitions are rejected in the service, not in views. The Authority's own capabilities are declared on `Authority`.

**2.5 Admin review and approval.** `MitigationActionPin`, `ActionType`. `TaskService.approve` runs as one atomic step: task `COMPLETED`, report `RESOLVED` with `resolved_note` copied (`Report.mark_resolved`), and a pin created at the same location with the Authority's note and the Admin's chosen `ActionType`. `send_back` returns the task to `ASSIGNED` with a remark. Resolved reports leave the heatmap automatically.

**2.6 Pins on the map.** `renderPins` layer in `map.js`. `ACTION_PIN_LIFETIME_HOURS` setting. Expired pins are deleted by a service method called on map page load (no scheduler). Admin can add pins manually, reusing `enablePinPicker`, and remove them.

**2.7 Advisories.** `Advisory` with `is_active(now)`, `AdvisoryService.post_advisory` and `get_active_advisories`. Admin post form. Active advisories are shown to everyone, with a banner or section on the home page. Expired ones are hidden.

**2.8 Verification.** Run SSD 3A and 3B end to end. Confirm hidden and resolved reports are off the heatmap, pins never add heat, pins disappear after the lifetime, Admin cannot accept tasks and Authority cannot approve. Re-run the Phase 1 flows.

## 5. Phase 3: Symptom Questionnaire and Medical Help Portal

**Goal:** a logged-in user takes the questionnaire, gets risk guidance (not diagnosis), and is taken to the right medical help.

**Plugs into Phase 1:** new `medical` app; `RegisteredUser` already carries the "take questionnaire" and "access portal" capabilities, declared here; one nav link (Questionnaire only, the portal has no menu link).

### Sub-phases

**3.0 Architecture review window.** Items #8 (questions, red-flag rules, scoring thresholds, all supplied by the owner), #14 (who loads thanas, providers, doctors, test info), #11 (admin UI for providers and doctors).

**3.1 Data models.** `RiskLevel`, `ProviderType`, `QuestionnaireResponse` (with user FK), `Thana`, `MedicalProvider`, `Doctor`, `TestInfo`. Migrations and seed fixtures per the #14 decision.

**3.2 Questionnaire and scoring.** `RiskScorer.has_red_flags` and `calculate_risk`. Red flags give `URGENT`; otherwise `LOW`, `MEDIUM` or `HIGH`. Form, save every submission, results page with advice and the "guidance, not diagnosis" disclaimer.

**3.3 Medical Help portal.** `MedicalPortalService.get_campus_options`, `get_outside_options(thana)`, `get_recommended_tests(risk)`. Campus view (doctor, building, room, contact, hours). Off-campus view (pick a thana, then hospitals, clinics and chambers with phone, hours and Google Maps link). Provider details page. Recommended tests by risk level.

**3.4 Result-to-portal flow.** `LOW` and `MEDIUM` show an optional continue link. `HIGH` and `URGENT` redirect straight to the portal with a CSS-only popup advising proper medical directives. The saved response keeps the exact risk level. The portal is not directly reachable from the menu.

**3.5 Doctor and provider management.** Admin adds and updates providers and doctors, using the approach settled in 3.0.

**3.6 Verification.** Run SSD 2 for red-flag and non-red-flag paths, check guest redirection to login, check lists and tables at phone width, and re-run earlier phases.

## 6. Phase 4: Volunteer Cleanup Portal

**Goal:** logged-in users create cleanup events, others join or leave, and everyone sees events on the map with their own pins.

**Plugs into Phase 1:** new `events` app; `renderEventPins` added to `map.js`; `enablePinPicker` reused for choosing the event location; Admin capabilities added on `Admin`.

### Sub-phases

**4.0 Architecture review window.** Item #9 (confirm only Admin updates status, not the creator). Also the status transition rule and whether the participant count is shown.

**4.1 Models.** `EventStatus`, `CleanupEvent`, `EventParticipation` with a unique constraint (one row per user per event).

**4.2 EventService.** `create_event`, `join_event`, `leave_event`, `remove_event(admin, event)`, `update_status(event, status)`. Status moves only `PLANNED` to `ONGOING` to `COMPLETED`, and invalid moves are rejected in the service.

**4.3 Event pages.** List and detail (responsive), create form (title, description, start `datetime-local`, map pin), join and leave buttons for users. Guests can view but cannot create or join.

**4.4 Map layer.** Event pins with a custom icon, separate from report markers and mitigation pins, and they never count toward heat. They are added through the new layer function and the heatmap view's context. No other map code changes.

**4.5 Admin controls.** Remove an event and update its status.

**4.6 Final verification.** Run all four features end to end on phone and desktop. Confirm role boundaries (Guest, Registered User, Authority, Admin), confirm no stray JS outside the map, confirm migrations are purely additive, and confirm the Section 12 out-of-scope list is respected.

## 7. Hand-off Between Phases

| Phase ends with | Next phase adds | How it connects |
| --- | --- | --- |
| User model, roles, permission mechanism, base template | Capabilities on `Admin` and `Authority`, nav links | One-line capability declarations and a link in the menu |
| `Report` with `active()` and the map shell | Moderation, tasks, pins | `hide()` and `RESOLVED` change what `active()` returns, so the map needs no changes |
| `map.js` layer functions and `enablePinPicker` | `renderPins`, `renderEventPins`, manual pin form, event form | New function plus a new `json_script` block, with no edits to existing functions |
| Phase 1 apps and URL structure | `workflow`, `advisories`, `medical`, `events` | Own models, services, views, templates, URL include, nav link |
| Migrations | Each phase's own models | New migration files only |

## 8. Items the Owner Must Supply

- **Before Phase 1:** campus boundary coordinates (and shape), daily report limit (confirmed during Phase 1).
- **Before Phase 2:** decisions on #4, #7, #11.
- **Before Phase 3:** questionnaire questions, red-flag rules, scoring thresholds, and who supplies the starting provider, doctor, thana and test data (#8, #14).
- **Before Phase 4:** confirmation of #9.
- **After approval:** record this phase list in Agent.md Section 10 and set open item #1 as resolved.
