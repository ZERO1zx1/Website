# CodeCraft Academy — Монгол хэлний дөрвөн замын curriculum blueprint

## 1. Зорилго ба сургалтын амлалт

CodeCraft Academy нь анхлан суралцагчийг зөвхөн syntax цээжлүүлэх биш, **өөрөө асуудлыг задлах, кодоо турших, алдаагаа унших, шийдлээ тайлбарлах, жижиг бүтээгдэхүүн болгон дуусгах** чадварт хүргэнэ. Суралцагч бүр lesson → жишээ → богино recall → guided exercise → bug lab → independent challenge → project гэсэн давталтаар явна.

Энэ бүтэц нь MDN-ийн шинэ front-end хөгжүүлэгчид зайлшгүй эзэмших чадварын дараалал болох web standards, semantic HTML, CSS fundamentals/text/layout, JavaScript fundamentals, accessibility, design болон version control-той нийцнэ [1]. Python зам нь албан ёсны Python Tutorial-ийн interpreter, үндсэн хэл, control flow, functions, data structures, modules, I/O, errors болон classes-ийн дарааллыг анхан шатны тайлбартайгаар өргөтгөнө [2].

> **Суралцагчийн гол дүрэм:** “Хариуг харахаасаа өмнө өөрийн таамгийг бич. Алдааг нуухын оронд алдааны мессежийг унш. Нэг ойлголтыг дор хаяж нэг өөрийн жишээгээр батал.”

## 2. Нэгдсэн суралцах journey

| Алхам | Суралцагчийн хийх зүйл | Платформын дэмжлэг | Дууссан гэж үзэх нотолгоо |
|---|---|---|---|
| Сэдэв нээх | 5–10 минутын Монгол тайлбар уншина | Mental model, жишээ, нэр томьёоны тайлбар | “Би үүнийг өөрийн үгээр хэлж чадна” хариулт |
| Шууд турших | Code Lab-д жишээг өөрчилнө | Starter code, Run, output/error panel | Код дор хаяж нэг удаа ажилласан |
| Ойлголтоо шалгах | 2–4 recall/quiz асуултад хариулна | Шууд feedback, буруу сонголтын тайлбар | 70%+ эсвэл дахин оролдлого |
| Дасгал хийх | Нэг зорилготой жижиг challenge дуусгана | Visible/hidden tests, hints, retry | Automated test pass |
| Алдаа засах | Bug Lab-д зориудын bug-ийг оношилно | Error category, step-by-step hint | Зассан code + тайлбарласан шалтгаан |
| Бие даах | Шинэ нөхцөлтэй independent challenge хийнэ | Test contract, submission history | Accepted submission |
| Бүтээх | Guided эсвэл portfolio project дуусгана | Milestone checklist, rubric, preview | Working demo, README, reflection |
| Эргэн санах | Өмнөх чадварыг spaced review-ээр сэргээнэ | Daily review queue, streak, XP | Өмнөх 3 ойлголтын богино review |

## 3. Path A — HTML: утга, бүтэц, хүртээмж

### Path outcome

Суралцагч semantic HTML ашиглан зөв бүтэцтэй, keyboard-оор ашиглаж болох, form ба content hierarchy-тэй веб хуудсыг бие даан байгуулна. Төгсгөлд нь accessibility checklist-ээр өөрийн хуудсыг шалгаж, CSS/JavaScript-д найдахгүйгээр утгатай HTML бүтэц гаргана.

| Module | Гол ойлголт | Lesson-үүд | Дасгал ба bug lab | Project |
|---|---|---|---|---|
| 1. Вэб хэрхэн ажилладаг вэ | Browser, URL, request/response, file structure | `index.html`-ээ нээх; browser developer tools; relative path | Broken link засах; буруу file path оношлох | Миний эхний profile page |
| 2. Semantic content | `doctype`, headings, paragraphs, lists, links, images | Уншигдах бүтэц; heading hierarchy; link vs button | Heading level bug; alt text нөхөх; navigation засах | Монгол нийтлэлийн page |
| 3. Layout-д бэлдэх бүтэц | `header`, `nav`, `main`, `section`, `article`, `aside`, `footer` | Component шиг бодох; reusable structure | Div soup refactor; landmark дутууг засах | Course landing page |
| 4. Forms ба user input | label, input, select, textarea, button, validation attributes | Form data ойлгох; accessible labels | Label холбоосгүй form; submit button type bug | Сургалтын бүртгэлийн form |
| 5. Media ба embedded content | image, figure, audio/video, iframe, responsive media | File size, alt, caption, fallback | Broken image, missing alt, iframe title | Монгол аяллын guide |
| 6. Accessibility ба publish readiness | keyboard, focus, semantic names, contrast awareness | Keyboard-only review; screen-reader mental model | Tab order bug; empty link; duplicate heading | WCAG-inspired audit-тэй portfolio page |
| 7. Independent build | Requirements унших, content hierarchy төлөвлөх | Specification-оос markup гаргах | Hidden structural checks | **Portfolio: Монгол хэлний event website** |

### HTML challenge-ийн жишээ

- `semantic-article`: Гарчиг, зохиогч, нийтлэгдсэн огноо, 3 хэсэгтэй нийтлэлийг semantic element-ээр бүтээ.
- `accessible-form`: Label бүр input-тэй зөв холбогдсон эсэхийг automated source test-ээр шалгуул.
- `bug-missing-alt`: `img`-ийн alt дутуу bug-ийг засаж, decorative image-д хоосон alt хэрэглэх ялгааг тайлбарла.
- `nav-keyboard`: Navigation дотор button-ыг anchor-аар буруу сольсноос үүссэн keyboard bug-ийг оношил.

## 4. Path B — CSS: системтэй харагдац ба responsive layout

### Path outcome

Суралцагч CSS cascade, selector, box model, typography, color, Flexbox, Grid, responsive breakpoint болон design token ашиглан олон дэлгэц дээр ажиллах интерфэйс бүтээнэ. Тэр зөвхөн “гоё харагдуулах” биш, **яагаад тухайн layout ажиллаж байгааг** тайлбарлана.

| Module | Гол ойлголт | Lesson-үүд | Дасгал ба bug lab | Project |
|---|---|---|---|---|
| 1. CSS сэтгэлгээ | Rule, selector, cascade, inheritance, specificity | Stylesheet холбох; selector унших; browser inspector | Specificity мөргөлдөөн; stylesheet path bug | Plain page makeover |
| 2. Box model | content, padding, border, margin, sizing | `box-sizing`, overflow, spacing scale | Width overflow; margin collapse; button box bug | Card collection |
| 3. Typography ба visual system | font, line-height, hierarchy, color, CSS variables | Token үүсгэх; readable type scale | Low contrast; line-height bug; inconsistent color | Design token board |
| 4. Flexbox | main/cross axis, alignment, gap, wrapping | Navbar, card row, centered layout | `justify-content` буруу; wrapping overflow | Responsive navigation |
| 5. Grid ба page layout | tracks, columns, areas, auto-fit | Dashboard, gallery, two-column layout | Mobile overflow; fixed width trap | Learning dashboard |
| 6. Responsive ба motion | media query, fluid sizing, reduced motion | Mobile-first; hover/focus; prefers-reduced-motion | Mobile nav bug; motion accessibility bug | Mobile-first landing page |
| 7. Independent build | Design spec-ийг tokens/layout/components болгох | CSS architecture ба refactor | Duplicate styles цэвэрлэх | **Portfolio: CodeCraft course dashboard** |

### CSS challenge-ийн жишээ

- `box-model-card`: Card-ийн нийт өргөн 320px хэвээр байхаар padding/border-ийг зөв тооц.
- `flex-navbar`: Desktop дээр нэг мөр, mobile дээр wrap болох navigation бүтээ.
- `grid-gallery`: 3/2/1 column responsive gallery хийж horizontal scroll-ийг арилгана.
- `theme-tokens`: Color-уудыг CSS custom property болгон салгаж light/dark theme бэлд.
- `bug-specificity`: Inline style ашиглалгүйгээр `.button-primary`-г зөв override хий.

## 5. Path C — JavaScript: interaction, state, API

### Path outcome

Суралцагч JavaScript-ийн суурь хэл, DOM, event, state, async request, error handling болон modular code ашиглан хэрэглэгчийн үйлдэлд хариу өгдөг frontend feature бүтээнэ. Тэр UI-г зөвхөн ажиллуулах бус, state-ийн урсгалыг зурж, error state-г хэрэглэгчид ойлгомжтой харуулна.

| Module | Гол ойлголт | Lesson-үүд | Дасгал ба bug lab | Project |
|---|---|---|---|---|
| 1. JavaScript хэлний суурь | values, variables, types, operators, conditionals | Console-оор турших; expression унших | Type coercion bug; boolean logic | Tip calculator |
| 2. Давталт ба function | loops, parameters, return, scope | Давталтаар data боловсруулах; жижиг function бичих | Return дутуу; infinite loop; scope bug | Score calculator |
| 3. Array, object, data model | map/filter/reduce basics, object shape, JSON | Data-г UI-д бэлдэх; immutable thinking | Wrong property; mutation bug | Course catalog filter |
| 4. DOM ба event | query, textContent, classList, event delegation | Safe DOM update; form interaction | `innerHTML` injection risk; wrong selector | Interactive todo list |
| 5. State ба UI rendering | single source of truth, render function, empty/loading/error | UI state-уудыг салгах | Stale state; duplicate event listener | Shopping/cart simulator |
| 6. Async ба API | fetch, JSON, HTTP status, try/catch, debounce | API response parse; loading/error feedback | HTML-as-JSON error; missing credentials | Search dashboard |
| 7. Modules ба quality | import/export, reusable helper, validation, testing mindset | Page module architecture; unit-like checks | Global variable collision | **Portfolio: Learning progress tracker** |

### JavaScript challenge-ийн жишээ

- `dom-counter`: Button бүр дарагдахад counter шинэчлэгдэж, DOM-д зөвхөн `textContent` ашиглан гарна.
- `filter-catalog`: Category filter нь empty state, active state, reset action-тай байна.
- `fetch-state`: loading, success, empty, error гэсэн дөрвөн UI state-г ялга.
- `bug-json-html`: API 500 үед HTML буцаахад `Unexpected token '<'` гардаг bug-ийг safe parser-аар зас.
- `keyboard-modal`: Escape болон focus return-тэй accessible modal interaction хий.

## 6. Path D — Python: логик, өгөгдөл, автоматжуулалт

### Path outcome

Суралцагч Python interpreter ашиглан жижиг скрипт бичиж, input/output, нөхцөл, давталт, function, data structure, file/JSON, exception, module болон class ойлголтыг practical project-д хэрэглэнэ. Тэр алдааны traceback-ийг уншиж, bug-ийг таамаг–туршилт–засвар гэсэн аргаар шийднэ.

| Module | Гол ойлголт | Lesson-үүд | Дасгал ба bug lab | Project |
|---|---|---|---|---|
| 1. Python-той танилцах | interpreter, script, values, variables, strings, numbers | `print`, input, f-string | String/number type bug | Мэндчилгээний CLI |
| 2. Condition ба loop | `if`, comparison, boolean, `for`, `while`, range | Decision tree; loop invariant | Off-by-one; infinite loop; wrong condition | Quiz score engine |
| 3. Function | parameter, return, default, scope, docstring | Function contract бичих | Return vs print; mutable default awareness | Expense calculator |
| 4. Data structures | list, tuple, set, dict, comprehension | Data modeling; lookup ба aggregation | KeyError; index error; duplicate handling | Student gradebook |
| 5. File ба JSON | read/write, encoding, structured data | Save/load state; JSON schema | File not found; malformed JSON | Habit tracker storage |
| 6. Errors ба debugging | syntax error, exception, traceback, raise, cleanup | Error category; defensive input | Bare except; wrong exception; hidden bug | Robust CLI utility |
| 7. Modules, packages ба classes | import, module path, class, instance, method | Project folder; separation of concern | Circular import; state leakage | **Portfolio: Personal learning tracker CLI** |

### Python challenge-ийн жишээ

- `greet-function`: `greet(name)` function нь хоосон нэрийг зөв зохицуулна.
- `grade-summary`: Dictionary-ээс дундаж, хамгийн өндөр, тэнцсэн суралцагчийг гаргана.
- `bug-index-error`: List-ийн сүүлийн элементийг буруу index ашиглан авч буй bug-ийг зас.
- `json-habit-tracker`: JSON файл байхгүй үед initial state үүсгэж, буруу JSON үед хэрэглэгчийн ойлгомжтой error өг.
- `module-refactor`: Нэг том script-ийг `models.py`, `storage.py`, `main.py` болгон салга.

## 7. Нэгдсэн project ladder

| Түвшин | Project | Хүрэх чадвар | Шалгах rubric |
|---|---|---|---|
| Guided 1 | Миний profile page | HTML structure, basic CSS | Semantic structure, headings, links, responsive minimum |
| Guided 2 | Responsive course card | Box model, Flexbox, tokens | No overflow, focus state, consistent spacing |
| Guided 3 | Interactive task board | DOM, event, state | Add/delete/filter, empty state, safe rendering |
| Guided 4 | Python CLI tracker | Functions, collections, JSON, errors | Valid input, persistence, modularity |
| Portfolio 1 | Монгол event website | HTML + CSS + accessibility | Responsive pages, semantic markup, keyboard review |
| Portfolio 2 | CodeCraft learning dashboard | JS + API + progress | Loading/error/empty states, API parsing, component separation |
| Portfolio 3 | Learning tracker CLI/API foundation | Python + data modeling | Tests, error handling, README, clean modules |
| Portfolio 4 | Full-stack capstone | Four paths combined | Product brief, Git history, demo, reflection, peer review |

## 8. Lesson бүрийн стандарт бүтэц

Нэг lesson дараах дарааллаар бичигдэнэ.

1. **Яагаад хэрэгтэй вэ?** — бодит бүтээгдэхүүн дэх хэрэглээ.
2. **Mental model** — шинэ ойлголтыг өдөр тутмын зүйрлэлээр тайлбарлана.
3. **Syntax биш contract** — input, output, invariant-ийг тодорхойлно.
4. **Worked example** — мөр бүрийн тайлбартай богино код.
5. **Try it** — суралцагч нэг утга өөрчилж үр дүнг таамаглана.
6. **Recall check** — хариуг шууд хэлэхгүй, санах дасгал.
7. **Practice challenge** — нэг зорилготой automated test.
8. **Bug Lab** — зориудын алдаа, error message, hint ladder.
9. **Reflection** — “ямар сонголт хийсэн, яагаад?” гэсэн богино тайлбар.
10. **Next step** — дараагийн lesson эсвэл project руу тодорхой холбоос.

## 9. Automated grading ба feedback policy

Automated test нь зөвхөн эцсийн output шалгахгүй. Source-level HTML/CSS requirement, runtime behavior, edge case, accessibility marker болон security-sensitive pattern-ийг тусдаа ангилна.

| Test layer | Жишээ | Суралцагчид өгөх feedback |
|---|---|---|
| Syntax | Код parse болох эсэх | Ямар мөрөнд syntax зөрсөн |
| Basic behavior | Үндсэн input/output | Expected vs actual output |
| Edge case | Empty, negative, long input | Яагаад энэ нөхцөлийг бодох хэрэгтэй |
| Structure | Semantic tag, function/module shape | Requirement дутуу байгааг нэрлэнэ |
| Accessibility | label, alt, keyboard-friendly control | Хэрэглэгчийн ямар саад үүсэхийг тайлбарлана |
| Security | Unsafe dynamic HTML, secret exposure | Аюултай pattern-ийг засах чиглэл өгнө |

Hint ladder нь эхлээд concept hint, дараа нь strategy hint, эцэст нь жижиг pseudocode өгнө. Бүтэн хариуг зөвхөн “solution review” шатанд харуулна. Accepted submission бүр XP өгнө; partial/rejected оролдлого нь streak-ийг таслахгүй ч XP-г давхар олгохгүй.

## 10. Сурагчийн бие даах чадварыг хэмжих үзүүлэлт

| Үзүүлэлт | Хэмжилт |
|---|---|
| Recall | Өмнөх ойлголтын review зөв хариултын хувь |
| Transfer | Шинэ нөхцөлтэй challenge-д hintгүй pass хийх хувь |
| Debugging | Error category зөв нэрлээд засах хугацаа |
| Independence | Нэг challenge-д ашигласан hint-ийн түвшин |
| Completion quality | Tests, accessibility, README, reflection rubric |
| Retention | 1, 3, 7 хоногийн дараах дахин шалгалт |

Dashboard нь эдгээрийг оноо болгон нуухын оронд “юуг аль хэдийн чаддаг, юуг дахин турших вэ?” гэсэн actionable feedback болгон харуулна.

## 11. Implementation backlog

| Priority | Implementation unit | Done criteria |
|---|---|---|
| P0 | Catalog schema-г `lesson`, `exercise`, `bug_lab`, `guided_project`, `portfolio_project`-ийг бүрэн илэрхийлэх болгох | Нэг normalized shape бүх page-д ашиглагдана |
| P0 | Path бүрт 7 module, эхний 3 module-ийн Монгол lesson content | 4 path × 10+ lesson render, slug unique |
| P0 | Challenge бүрт visible/hidden test, hint ladder, XP | Accepted/rejected/partial feedback ажиллана |
| P1 | Bug Lab evaluator ба error category | Syntax, runtime, logic, structure ангилал гарна |
| P1 | Project rubric/checklist | Milestone completion server-side хадгалагдана |
| P1 | Review queue/spaced review | Dashboard өмнөх чадварыг дахин санал болгоно |
| P2 | Teacher/peer feedback | Project reflection болон rubric comment хадгалагдана |
| P2 | Search, tags, difficulty, language filters | Challenge catalog-ийг хайж шүүнэ |

## References

[1]: https://developer.mozilla.org/en-US/curriculum/ "MDN Curriculum"

[2]: https://docs.python.org/3/tutorial/ "The Python Tutorial — Python documentation"

[3]: https://www.w3.org/WAI/fundamentals/accessibility-intro/ "Introduction to Web Accessibility — W3C WAI"

[4]: https://www.boot.dev/ "Boot.dev public learning experience"
