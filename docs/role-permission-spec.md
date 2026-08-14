# Role and permission specification

## Scope

This specification defines the platform roles, effective permissions and approval rules for the Codehaven backend. Role names are machine-stable English identifiers; human-facing labels use the approved bilingual glossary.

## Role hierarchy

| Role | Монгол нэр | Scope | Description |
|---|---|---|---|
| `owner` | Эзэмшигч | Platform | Website-ийн бүрэн эзэмшигч. Platform settings, owner-level role assignment, audit болон бүх operational resource-ийг удирдана. |
| `admin` | Администратор | Platform operations | Хэрэглэгч, багшийн хүсэлт, сургалтын resource болон moderation-ийг удирдана. Owner эрхийг өөрчилж чадахгүй. |
| `teacher` | Багш | Assigned classes | Өөрийн сургалт, анги, бодлого, суралцагчийн ахиц болон багшийн самбарыг удирдана. |
| `student` | Суралцагч | Own account/data | Өөрийн сургалт, бодлого, илгээлт, ахиц болон профайлыг ашиглана. |

## Permission matrix

| Permission | Owner | Admin | Teacher | Student |
|---|:---:|:---:|:---:|:---:|
| `platform.read` | ✓ | ✓ | — | — |
| `platform.settings.manage` | ✓ | — | — | — |
| `users.read` | ✓ | ✓ | Assigned | Own |
| `users.manage` | ✓ | ✓ | — | — |
| `roles.manage` | ✓ | Limited | — | — |
| `owner.manage` | ✓ | — | — | — |
| `teachers.approve` | ✓ | ✓ | — | — |
| `courses.read` | ✓ | ✓ | ✓ | ✓ |
| `courses.manage` | ✓ | ✓ | Own | — |
| `classes.manage` | ✓ | ✓ | Own | — |
| `problems.read` | ✓ | ✓ | ✓ | ✓ |
| `problems.manage` | ✓ | ✓ | Own | — |
| `submissions.create` | ✓ | ✓ | ✓ | ✓ |
| `submissions.read` | ✓ | ✓ | Assigned | Own |
| `analytics.read` | ✓ | ✓ | Assigned | Own |
| `teacher.dashboard.read` | ✓ | ✓ | ✓ | — |
| `student.dashboard.read` | ✓ | ✓ | — | ✓ |
| `audit.read` | ✓ | ✓ | — | — |

## Approval rules

A public registration always creates an effective `student` account. A student may submit a teacher request, but the request is stored as `requested_role = teacher` with `approval_status = pending`; the effective role remains `student` until an owner or admin approves it. Rejection keeps the effective role as `student` and records the rejection status.

Only the owner may grant or revoke the `owner` role. An admin may manage operational roles but cannot promote a user to owner, demote the owner, or modify owner permissions. Every role change must record the actor, target, previous role, new role, reason and timestamp.

## API response contract

Every error should include a stable English code and bilingual messages:

```json
{
  "error": {
    "code": "permission_denied",
    "message": "You do not have permission to perform this action.",
    "message_mn": "Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна."
  }
}
```

The frontend may display `message_mn` when the selected locale is `mn`, but the stable `code` remains the integration key.

## Approved glossary

| English | Монгол | Usage |
|---|---|---|
| role | үүрэг | Хэрэглэгчийн систем дэх ангилал |
| permission | зөвшөөрөл | Тодорхой үйлдэл хийх эрх |
| owner | эзэмшигч | Website-ийн дээд түвшний эзэмшигч |
| admin | администратор | Системийн үйл ажиллагааны удирдагч |
| teacher | багш | Сургалт, анги удирдагч |
| student | суралцагч | Суралцагч хэрэглэгч |
| dashboard | хяналтын самбар | Тойм мэдээлэл харах үндсэн дэлгэц |
| teacher panel | багшийн самбар | Багшийн анги, ахицын удирдлага |
| approval | баталгаажуулалт | Хүсэлтийг зөвшөөрөх процесс |
| submission | илгээлт | Суралцагчийн илгээсэн код/хариу |
| course | сургалт | Дээд түвшний сургалтын багц |
| class | анги | Тодорхой багшийн сургалтын бүлэг |
| lesson | хичээл | Сургалтын нэгж |
| problem | бодлого | Код бичиж шийдэх даалгавар |
| mastery | эзэмшил | Ур чадварын эзэмшсэн түвшин |
| audit log | аудитын бүртгэл | Эрх болон үйлдлийн өөрчлөлтийн түүх |
