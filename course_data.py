# CodeCraft Academy Course Data
# Contains the detailed curriculum for Python, HTML, CSS, and JavaScript based on the provided PDF materials.

COURSE_CATALOG = {
    'python': {
        'id': 'python',
        'title': 'Python foundations',
        'icon': 'Py',
        'color': 'purple',
        'eyebrow': 'Програмчлалын сэтгэлгээ',
        'duration': '6 долоо хоног',
        'level': 'Анхан шат',
        'description': 'Код хэрхэн ажилладгийг ойлгож, логик сэтгэлгээ болон асуудал задлах сууриа тавина.',
        'modules': [
            {
                'title': '01 · Эхлэл',
                'summary': 'Орчин, өгөгдөл, гаралт',
                'lessons': [
                    {
                        'id': 'py-start',
                        'title': 'Python гэж юу вэ?',
                        'outcome': 'Код, програм, interpreter-ийн ялгааг ойлгоно.',
                        'task': 'print(), variable, arithmetic ашигласан 5 мөртэй анхны script бич.',
                        'minutes': 20,
                        'language': 'python',
                        'unit': 'UNIT 01',
                        'concept': '<p>Python нь өндөр түвшний, ерөнхий зориулалтын programming language. Кодыг уншихад хялбар болгох syntax болон өргөн standard library-аараа хүчтэй. Python source файл ихэвчлэн <code>.py</code> өргөтгөлтэй. Interpreter source-ийг bytecode болгон хөрвүүлж, runtime орчин дээр ажиллуулдаг гэж энгийнээр ойлгож болно.</p>',
                        'mental_model': 'Source code = чиний бичсэн заавар. Bytecode = Python runtime-д ойр intermediate хэлбэр. Runtime = эдгээр instruction-ийг ажиллуулж object, memory, function call-ийг удирдах орчин.',
                        'code': 'print("Сайн байна уу, CodeCraft Academy!")\n\nprice = 12500\nquantity = 3\nprint("Нийт:", price * quantity, "₮")',
                        'mistake': 'Python-ийг зөвхөн "interpreted тул удаан" гэсэн нэг өгүүлбэрээр ойлгох. Runtime model илүү нарийн.',
                        'best_practice': 'Эхний өдрөөс terminal/IDE дээр кодоо өөрөө ажиллуулж output болон error message унш.',
                        'quiz': {
                            'question': 'Python код ажиллах үндсэн 3 үе шат юу вэ?',
                            'answer': 'Source code -> Bytecode -> Runtime (Execution).'
                        }
                    },
                    {
                        'id': 'py-values',
                        'title': 'Data types (int, float, bool, str)',
                        'outcome': 'int, float, bool, str, None төрлүүдийг зөв сонгоно.',
                        'task': 'Өөрийн нэр, нас, хот, сурагч эсэх, сонгосон хичээл гэсэн 5 variable үүсгэ.',
                        'minutes': 20,
                        'language': 'python',
                        'unit': 'UNIT 01',
                        'concept': '<p>Program доторх value бүр төрөлтэй. Төрөл нь ямар operation зөвшөөрөгдөх, хэрхэн харьцуулах, хэрхэн format хийхэд нөлөөлнө. <code>int</code> бүхэл тоо, <code>float</code> бутархай, <code>bool</code> True/False, <code>str</code> текст, <code>None</code> "утга алга/одоогоор сонгогдоогүй" гэсэн тусгай object.</p>',
                        'mental_model': 'Variable нь type бүхий хайрцаг гэхээс илүү name -> object binding гэж бод. Нэг нэр дараа нь өөр type object руу bind хийж болно.',
                        'code': 'age = 16\nprice = 12999.50\nis_member = True\ncity = "Улаанбаатар"\nselected_course = None\n\nprint(type(age))\nprint(type(city))',
                        'mistake': 'true/false гэж JavaScript шиг жижиг үсгээр бичих.',
                        'best_practice': 'Type-ийг нэрээр цээжлэхээс илүү тухайн value дээр ямар operation хийхээ бод.',
                        'quiz': {
                            'question': 'Текстэн утгыг ямар төрлөөр хадгалдаг вэ?',
                            'answer': 'String буюу str төрлөөр хадгална.'
                        }
                    },
                    {
                        'id': 'py-list',
                        'title': 'List-ийн эхлэл',
                        'outcome': 'List-д утга нэмж, хасаж, хандана.',
                        'task': '5 хичээлийн list үүсгээд 1-ийг нэм, 1-ийг хас, эхний/сүүлийн утгыг хэвлэ.',
                        'minutes': 20,
                        'language': 'python',
                        'unit': 'UNIT 01',
                        'concept': '<p>List бол олон value-г дарааллаар хадгалах, өөрчилж нэмэх/хасах боломжтой хамгийн түгээмэл collection. Квадрат хаалтаар үүснэ. Index 0-оос эхэлнэ. Duplicate value зөвшөөрнө. append/remove/pop зэрэг method-оор өөрчилж болно.</p>',
                        'mental_model': 'List = дараалалтай, өөрчлөгдөх боломжтой "ажлын жагсаалт". Course list, scores, tasks зэрэгт тохиромжтой.',
                        'code': 'courses = ["HTML", "CSS", "Python"]\ncourses.append("JavaScript")\nprint(courses[0])\nprint(courses[-1])\n\ncourses.remove("CSS")\nprint(courses)',
                        'mistake': 'List-ийг "array-тай яг адил" гэж бүх хэл дээр ижил гэж ойлгох.',
                        'best_practice': 'Data ordered + mutable байх хэрэгтэй үед list сонго.',
                        'quiz': {
                            'question': 'List-ийн эхний элементийн index хэд байдаг вэ?',
                            'answer': '0 (тэг) байдаг.'
                        }
                    }
                ]
            },
            {
                'title': '02 · Логик',
                'summary': 'Нөхцөл, давталт, алдаа',
                'lessons': [
                    {
                        'id': 'py-if',
                        'title': 'Нөхцөл шалгах (if/elif/else)',
                        'outcome': 'if, elif, else ашиглан шийдвэр гаргана.',
                        'task': 'Оноог үсгэн үнэлгээнд хөрвүүл.',
                        'minutes': 20,
                        'language': 'python',
                        'unit': 'UNIT 02',
                        'concept': '<p>Програмын урсгалыг Boolean (True/False) утга дээр үндэслэн өөрчилдөг. <code>if</code> нь нөхцөл үнэн үед, <code>elif</code> нь өмнөх нөхцөл худал үед дараагийн нөхцөлийг шалгах, <code>else</code> нь бүх нөхцөл худал үед ажиллана.</p>',
                        'mental_model': 'Яг л уулзвар дээр зогсоод аль замаар явахаа шийдэж байгаатай адил. Зөвхөн нэг л замыг сонгоно.',
                        'code': 'score = 86\nif score >= 90:\n    print("A")\nelif score >= 80:\n    print("B")\nelse:\n    print("Keep going")',
                        'mistake': 'Буруу догол мөр (indentation) ашиглаж IndentationError гаргах.',
                        'best_practice': 'Хамгийн нарийн/тусгай нөхцөлөөс эхэлж шалгах хэрэгтэй.',
                        'quiz': {
                            'question': 'Хэрвээ бүх if болон elif нөхцөл худал байвал аль блок ажиллах вэ?',
                            'answer': 'else блок ажиллана.'
                        }
                    }
                ]
            }
        ]
    },
    'html': {
        'id': 'html',
        'title': 'HTML essentials',
        'icon': '<>',
        'color': 'orange',
        'eyebrow': 'Вэбийн утга ба бүтэц',
        'duration': '4 долоо хоног',
        'level': 'Анхан шат',
        'description': 'Хүртээмжтэй, хайлтын системд ойлгомжтой веб хуудсыг зөв бүтцээр байгуулна.',
        'modules': [
            {
                'title': '01 · Вэбийн суурь',
                'summary': 'Browser ба document',
                'lessons': [
                    {
                        'id': 'html-web',
                        'title': 'Вэб хэрхэн ажилладаг вэ?',
                        'outcome': 'Browser, server, URL, request-ийн үүргийг ойлгоно.',
                        'task': 'Нэг web request-ийн урсгалыг зур.',
                        'minutes': 18,
                        'language': 'html',
                        'unit': 'HTML 01',
                        'concept': '<p>HTML (HyperText Markup Language) нь вэб хуудасны араг ясыг бүрдүүлдэг. Browser (Chrome, Safari гэх мэт) нь HTML файлыг уншиж, хэрэглэгчид харагдахуйц вэб хуудас болгон хувиргадаг. Вэб хуудас бол баримт бичиг (document) юм.</p>',
                        'mental_model': 'HTML бол барилгын тоосго, цемент юм. Ямар ч гоёл чимэглэлгүй зөвхөн хана, хаалга, цонх хаана байхыг заана.',
                        'code': '<!DOCTYPE html>\n<html>\n  <head>\n    <title>Миний анхны вэб</title>\n  </head>\n  <body>\n    <h1>Сайн уу!</h1>\n  </body>\n</html>',
                        'mistake': 'HTML-ийг програмчлалын хэл гэж андуурах. Энэ бол зөвхөн тэмдэглэгээт (markup) хэл юм.',
                        'best_practice': 'Үргэлж semantic буюу утга төгөлдөр tag ашиглахыг хичээгээрэй (жишээ нь div-ийн оронд main эсвэл article).',
                        'quiz': {
                            'question': 'HTML юуны товчлол вэ?',
                            'answer': 'HyperText Markup Language'
                        }
                    },
                    {
                        'id': 'html-tags',
                        'title': 'Tags ба Elements',
                        'outcome': 'HTML tag-уудыг зөв нээж, хааж сурна.',
                        'task': 'Гарчиг, догол мөр, холбоос бүхий энгийн хуудас үүсгэ.',
                        'minutes': 20,
                        'language': 'html',
                        'unit': 'HTML 01',
                        'concept': '<p>HTML element нь ихэвчлэн нээх tag, агуулга, хаах tag-аас бүрдэнэ. Жишээ нь: <code>&lt;p&gt;Догол мөр&lt;/p&gt;</code>. Зарим tag-ууд хаах tag-гүй (empty elements) байдаг, жишээ нь <code>&lt;br&gt;</code> эсвэл <code>&lt;img&gt;</code>.</p>',
                        'mental_model': 'Tag-ууд бол хайрцагнууд. Хайрцаг дотор өөр хайрцаг хийж (nested) болно.',
                        'code': '<h1>Том гарчиг</h1>\n<p>Энэ бол догол мөр. <br> Энэ бол шинэ мөр.</p>\n<a href="https://google.com">Google рүү очих</a>',
                        'mistake': 'Хаах tag-ийг мартах (жишээ нь <code>&lt;p&gt;Текст</code> гээд орхих).',
                        'best_practice': 'Кодоо үргэлж зөв догол мөрөөр (indentation) бичиж, уншихад хялбар болго.',
                        'quiz': {
                            'question': 'Холбоос үүсгэдэг tag юу вэ?',
                            'answer': '<a> tag (anchor).'
                        }
                    }
                ]
            }
        ]
    },
    'css': {
        'id': 'css',
        'title': 'CSS styling',
        'icon': '#',
        'color': 'pink',
        'eyebrow': 'Өнгө төрх ба байрлал',
        'duration': '4 долоо хоног',
        'level': 'Анхан шат',
        'description': 'Дизайн систем, responsive layout, animation ашиглан үзэмжтэй вэб бүтээнэ.',
        'modules': [
            {
                'title': '01 · CSS Үндэс',
                'summary': 'Өнгө, фонт, хэмжээ',
                'lessons': [
                    {
                        'id': 'css-intro',
                        'title': 'CSS гэж юу вэ?',
                        'outcome': 'Selector, property, value гурвыг ялгана.',
                        'task': 'h1 гарчгийн өнгийг цэнхэр болго.',
                        'minutes': 15,
                        'language': 'css',
                        'unit': 'CSS 01',
                        'concept': '<p>CSS (Cascading Style Sheets) нь HTML-ээр барьсан араг ясыг гоёж чимэглэх зориулалттай. Өнгө, фонт, байрлал, хөдөлгөөн зэргийг CSS-ээр тохируулдаг.</p>',
                        'mental_model': 'Хэрэв HTML нь барилгын хана бол CSS нь тэр ханыг будах будаг, обой, дотоод засал чимэглэл юм.',
                        'code': 'h1 {\n  color: blue;\n  font-size: 24px;\n  text-align: center;\n}',
                        'mistake': 'Бүх элементэд inline style буюу HTML дотор нь шууд style бичих.',
                        'best_practice': 'CSS кодыг үргэлж тусдаа .css файлд бичиж HTML-тэйгээ холбох нь цэгцтэй байдаг.',
                        'quiz': {
                            'question': 'CSS-д элементийг хэрхэн сонгож авдаг вэ?',
                            'answer': 'Selector ашиглаж сонгоно (жишээ нь: tag name, .class, #id).'
                        }
                    },
                    {
                        'id': 'css-box-model',
                        'title': 'Box Model (Хайрцгийн загвар)',
                        'outcome': 'Margin, padding, border-ийн ялгааг ойлгоно.',
                        'task': 'Хайрцаг үүсгээд padding, border, margin өг.',
                        'minutes': 25,
                        'language': 'css',
                        'unit': 'CSS 01',
                        'concept': '<p>HTML элемент бүр хайрцаг хэлбэртэй байдаг. Энэ хайрцаг нь Content (агуулга), Padding (дотор зай), Border (хүрээ), Margin (гадна зай) гэсэн 4 хэсгээс бүрдэнэ.</p>',
                        'mental_model': 'Зураг өлгөхтэй адил: Зураг (Content), жаазны шил хүртэлх зай (Padding), жааз өөрөө (Border), бусад зураг хүртэлх зай (Margin).',
                        'code': '.box {\n  width: 200px;\n  padding: 20px;\n  border: 2px solid black;\n  margin: 15px;\n}',
                        'mistake': 'Width-д padding болон border ордоггүйг мартах (box-sizing: border-box ашиглахгүй байх).',
                        'best_practice': 'Бүх элементэд `box-sizing: border-box;` тохируулж хэмжээ тооцоолохыг хялбар болго.',
                        'quiz': {
                            'question': 'Элементийн дотор талын зайг юу гэж нэрлэдэг вэ?',
                            'answer': 'Padding.'
                        }
                    }
                ]
            }
        ]
    },
    'javascript': {
        'id': 'javascript',
        'title': 'JavaScript basics',
        'icon': 'JS',
        'color': 'blue',
        'eyebrow': 'Динамик үйлдэл',
        'duration': '6 долоо хоног',
        'level': 'Дунд шат',
        'description': 'Вэб хуудсыг амьд болгож, хэрэглэгчтэй харилцах логик бичиж сурна.',
        'modules': [
            {
                'title': '01 · JS Үндэс',
                'summary': 'DOM ба хувьсагч',
                'lessons': [
                    {
                        'id': 'js-intro',
                        'title': 'JavaScript-ийн үүрэг',
                        'outcome': 'Вэб хуудсанд интерактив үйлдэл нэмнэ.',
                        'task': 'Товч дарахад alert гаргадаг код бич.',
                        'minutes': 25,
                        'language': 'javascript',
                        'unit': 'JS 01',
                        'concept': '<p>JavaScript бол вэб хуудсыг амьд, интерактив болгодог програмчлалын хэл юм. Хэрэглэгчийн үйлдэлд (товч дарах, хулгана хөдөлгөх) хариу үйлдэл үзүүлэхэд ашиглана.</p>',
                        'mental_model': 'HTML барилга, CSS засал чимэглэл бол JavaScript нь тэр барилгын цахилгаан, ус, гэрлийн унтраалга зэрэг амьд систем нь юм.',
                        'code': 'const button = document.querySelector("button");\n\nbutton.addEventListener("click", () => {\n  alert("Сайн байна уу!");\n});',
                        'mistake': 'var ашиглан хувьсагч зарлах. Орчин үед let болон const ашигладаг болсон.',
                        'best_practice': 'Өөрчлөгдөхгүй утгад үргэлж const ашиглах.',
                        'quiz': {
                            'question': 'HTML элементийг JS-ээр хэрхэн барьж авдаг вэ?',
                            'answer': 'document.querySelector() эсвэл document.getElementById() ашиглан.'
                        }
                    },
                    {
                        'id': 'js-dom-p5',
                        'title': 'DOM ба Интерактив',
                        'outcome': 'DOM элементүүдийг өөрчилж, event сонсож сурна.',
                        'task': 'Оноо нэмдэг энгийн тоглоомын логик бич.',
                        'minutes': 30,
                        'language': 'javascript',
                        'unit': 'JS 01',
                        'concept': '<p>DOM (Document Object Model) нь HTML хуудсыг JavaScript-аас удирдах боломжтой мод (tree) бүтэц юм. Бид DOM-ийг ашиглан текстийг өөрчлөх, товч дарахыг мэдрэх, шинэ элемент нэмэх боломжтой.</p>',
                        'mental_model': 'DOM бол вэб хуудасны "алсын удирдлага". JS-ээр товч дарж хуудсыг өөрчилнө.',
                        'code': 'let score = 0;\nconst scoreElement = document.querySelector("#score-value");\nconst target = document.querySelector("#target");\n\ntarget.addEventListener("click", () => {\n  score++;\n  scoreElement.innerText = score;\n});',
                        'mistake': 'Event listener-ийг элемент нь ачаалагдахаас өмнө нэмэх.',
                        'best_practice': 'DOM элементүүдийг хувьсагчид хадгалж аваад дараа нь ашиглах.',
                        'quiz': {
                            'question': 'Товч дарах үйлдлийг хэрхэн барьж авах вэ?',
                            'answer': 'addEventListener("click", ...) ашиглан.'
                        }
                    }
                ]
            }
        ]
    }
}

for _course in COURSE_CATALOG.values():
    _course['lesson_count'] = sum(len(module['lessons']) for module in _course['modules'])
    _course['first_lesson'] = _course['modules'][0]['lessons'][0]['id']
