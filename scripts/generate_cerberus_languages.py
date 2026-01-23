#!/usr/bin/env python3
"""
Generate comprehensive language database for Cerberus Hydra Defense.
Creates mappings for 50 human languages and 50 programming languages.
"""

import json
from pathlib import Path

# 50 Human languages with security message translations
HUMAN_LANGUAGES = {
    "en": {"name": "English", "alert_prefix": "SECURITY ALERT", "agent_spawned": "Defense agent spawned", "lockdown_initiated": "System lockdown initiated", "bypass_detected": "Security bypass detected", "section_locked": "Section locked"},
    "es": {"name": "Spanish", "alert_prefix": "ALERTA DE SEGURIDAD", "agent_spawned": "Agente de defensa generado", "lockdown_initiated": "Bloqueo del sistema iniciado", "bypass_detected": "Bypass de seguridad detectado", "section_locked": "Sección bloqueada"},
    "fr": {"name": "French", "alert_prefix": "ALERTE DE SÉCURITÉ", "agent_spawned": "Agent de défense créé", "lockdown_initiated": "Verrouillage du système initié", "bypass_detected": "Contournement de sécurité détecté", "section_locked": "Section verrouillée"},
    "de": {"name": "German", "alert_prefix": "SICHERHEITSWARNUNG", "agent_spawned": "Verteidigungsagent erzeugt", "lockdown_initiated": "Systemsperre eingeleitet", "bypass_detected": "Sicherheitsumgehung erkannt", "section_locked": "Abschnitt gesperrt"},
    "zh": {"name": "Chinese", "alert_prefix": "安全警报", "agent_spawned": "防御代理已生成", "lockdown_initiated": "系统锁定已启动", "bypass_detected": "检测到安全绕过", "section_locked": "区域已锁定"},
    "ja": {"name": "Japanese", "alert_prefix": "セキュリティ警告", "agent_spawned": "防御エージェント生成", "lockdown_initiated": "システムロックダウン開始", "bypass_detected": "セキュリティバイパス検出", "section_locked": "セクションロック"},
    "ar": {"name": "Arabic", "alert_prefix": "تنبيه أمني", "agent_spawned": "تم إنشاء وكيل الدفاع", "lockdown_initiated": "بدء إغلاق النظام", "bypass_detected": "تم اكتشاف تجاوز أمني", "section_locked": "القسم مقفل"},
    "ru": {"name": "Russian", "alert_prefix": "ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ", "agent_spawned": "Защитный агент создан", "lockdown_initiated": "Блокировка системы инициирована", "bypass_detected": "Обнаружен обход безопасности", "section_locked": "Раздел заблокирован"},
    "pt": {"name": "Portuguese", "alert_prefix": "ALERTA DE SEGURANÇA", "agent_spawned": "Agente de defesa gerado", "lockdown_initiated": "Bloqueio do sistema iniciado", "bypass_detected": "Bypass de segurança detectado", "section_locked": "Seção bloqueada"},
    "it": {"name": "Italian", "alert_prefix": "AVVISO DI SICUREZZA", "agent_spawned": "Agente di difesa creato", "lockdown_initiated": "Blocco sistema avviato", "bypass_detected": "Bypass di sicurezza rilevato", "section_locked": "Sezione bloccata"},
    "ko": {"name": "Korean", "alert_prefix": "보안 경고", "agent_spawned": "방어 에이전트 생성됨", "lockdown_initiated": "시스템 잠금 시작됨", "bypass_detected": "보안 우회 감지됨", "section_locked": "섹션 잠김"},
    "hi": {"name": "Hindi", "alert_prefix": "सुरक्षा चेतावनी", "agent_spawned": "रक्षा एजेंट उत्पन्न", "lockdown_initiated": "सिस्टम लॉकडाउन शुरू", "bypass_detected": "सुरक्षा बाईपास का पता चला", "section_locked": "अनुभाग लॉक"},
    "nl": {"name": "Dutch", "alert_prefix": "BEVEILIGINGSWAARSCHUWING", "agent_spawned": "Verdedigingsagent gegenereerd", "lockdown_initiated": "Systeem lockdown geïnitieerd", "bypass_detected": "Beveiligingsomzeiling gedetecteerd", "section_locked": "Sectie vergrendeld"},
    "tr": {"name": "Turkish", "alert_prefix": "GÜVENLİK UYARISI", "agent_spawned": "Savunma ajanı oluşturuldu", "lockdown_initiated": "Sistem kilitleme başlatıldı", "bypass_detected": "Güvenlik atlatma tespit edildi", "section_locked": "Bölüm kilitlendi"},
    "pl": {"name": "Polish", "alert_prefix": "OSTRZEŻENIE BEZPIECZEŃSTWA", "agent_spawned": "Agent obronny utworzony", "lockdown_initiated": "Blokada systemu zainicjowana", "bypass_detected": "Wykryto obejście zabezpieczeń", "section_locked": "Sekcja zablokowana"},
    "sv": {"name": "Swedish", "alert_prefix": "SÄKERHETSVARNING", "agent_spawned": "Försvarsagent skapad", "lockdown_initiated": "Systemlåsning initierad", "bypass_detected": "Säkerhetsförbikoppling upptäckt", "section_locked": "Avsnitt låst"},
    "no": {"name": "Norwegian", "alert_prefix": "SIKKERHETSVARSEL", "agent_spawned": "Forsvarsagent opprettet", "lockdown_initiated": "Systemnedlåsing igangsatt", "bypass_detected": "Sikkerhetsomgåelse oppdaget", "section_locked": "Seksjon låst"},
    "da": {"name": "Danish", "alert_prefix": "SIKKERHEDSADVARSEL", "agent_spawned": "Forsvarsagent oprettet", "lockdown_initiated": "Systemlåsning iværksat", "bypass_detected": "Sikkerhedsomgåelse opdaget", "section_locked": "Sektion låst"},
    "fi": {"name": "Finnish", "alert_prefix": "TURVALLISUUSVAROITUS", "agent_spawned": "Puolustusagentti luotu", "lockdown_initiated": "Järjestelmän lukitus aloitettu", "bypass_detected": "Turvallisuuden ohitus havaittu", "section_locked": "Osio lukittu"},
    "el": {"name": "Greek", "alert_prefix": "ΕΙΔΟΠΟΙΗΣΗ ΑΣΦΑΛΕΙΑΣ", "agent_spawned": "Παράγοντας άμυνας δημιουργήθηκε", "lockdown_initiated": "Κλείδωμα συστήματος ξεκίνησε", "bypass_detected": "Ανιχνεύθηκε παράκαμψη ασφαλείας", "section_locked": "Τμήμα κλειδώθηκε"},
    "cs": {"name": "Czech", "alert_prefix": "BEZPEČNOSTNÍ UPOZORNĚNÍ", "agent_spawned": "Obranný agent vytvořen", "lockdown_initiated": "Uzamčení systému zahájeno", "bypass_detected": "Zjištěno obejití zabezpečení", "section_locked": "Sekce uzamčena"},
    "hu": {"name": "Hungarian", "alert_prefix": "BIZTONSÁGI FIGYELMEZTETÉS", "agent_spawned": "Védelmi ügynök létrehozva", "lockdown_initiated": "Rendszer zárolás kezdeményezve", "bypass_detected": "Biztonsági megkerülés észlelve", "section_locked": "Szekció zárolva"},
    "ro": {"name": "Romanian", "alert_prefix": "ALERTĂ DE SECURITATE", "agent_spawned": "Agent de apărare generat", "lockdown_initiated": "Blocare sistem inițiată", "bypass_detected": "Bypass de securitate detectat", "section_locked": "Secțiune blocată"},
    "th": {"name": "Thai", "alert_prefix": "การแจ้งเตือนความปลอดภัย", "agent_spawned": "สร้างตัวแทนการป้องกันแล้ว", "lockdown_initiated": "เริ่มการล็อคระบบแล้ว", "bypass_detected": "ตรวจพบการหลีกเลี่ยงความปลอดภัย", "section_locked": "ส่วนถูกล็อค"},
    "vi": {"name": "Vietnamese", "alert_prefix": "CẢNH BÁO BẢO MẬT", "agent_spawned": "Tác nhân phòng thủ đã được tạo", "lockdown_initiated": "Khóa hệ thống đã được bắt đầu", "bypass_detected": "Phát hiện vượt qua bảo mật", "section_locked": "Phần đã khóa"},
    "id": {"name": "Indonesian", "alert_prefix": "PERINGATAN KEAMANAN", "agent_spawned": "Agen pertahanan dibuat", "lockdown_initiated": "Penguncian sistem dimulai", "bypass_detected": "Bypass keamanan terdeteksi", "section_locked": "Bagian terkunci"},
    "ms": {"name": "Malay", "alert_prefix": "AMARAN KESELAMATAN", "agent_spawned": "Agen pertahanan dijana", "lockdown_initiated": "Penutupan sistem dimulakan", "bypass_detected": "Pintasan keselamatan dikesan", "section_locked": "Bahagian dikunci"},
    "he": {"name": "Hebrew", "alert_prefix": "התראת אבטחה", "agent_spawned": "סוכן הגנה נוצר", "lockdown_initiated": "נעילת מערכת הופעלה", "bypass_detected": "זוהה עקיפת אבטחה", "section_locked": "מקטע נעול"},
    "fa": {"name": "Persian", "alert_prefix": "هشدار امنیتی", "agent_spawned": "عامل دفاعی ایجاد شد", "lockdown_initiated": "قفل سیستم آغاز شد", "bypass_detected": "دور زدن امنیتی شناسایی شد", "section_locked": "بخش قفل شد"},
    "uk": {"name": "Ukrainian", "alert_prefix": "ПОПЕРЕДЖЕННЯ БЕЗПЕКИ", "agent_spawned": "Захисний агент створено", "lockdown_initiated": "Блокування системи ініційовано", "bypass_detected": "Виявлено обхід безпеки", "section_locked": "Розділ заблоковано"},
    "bn": {"name": "Bengali", "alert_prefix": "নিরাপত্তা সতর্কতা", "agent_spawned": "প্রতিরক্ষা এজেন্ট তৈরি হয়েছে", "lockdown_initiated": "সিস্টেম লকডাউন শুরু হয়েছে", "bypass_detected": "নিরাপত্তা বাইপাস সনাক্ত করা হয়েছে", "section_locked": "বিভাগ লক করা হয়েছে"},
    "ta": {"name": "Tamil", "alert_prefix": "பாதுகாப்பு எச்சரிக்கை", "agent_spawned": "பாதுகாப்பு முகவர் உருவாக்கப்பட்டது", "lockdown_initiated": "அமைப்பு பூட்டல் தொடங்கப்பட்டது", "bypass_detected": "பாதுகாப்பு தவிர்ப்பு கண்டறியப்பட்டது", "section_locked": "பகுதி பூட்டப்பட்டது"},
    "te": {"name": "Telugu", "alert_prefix": "భద్రత హెచ్చరిక", "agent_spawned": "రక్షణ ఏజెంట్ సృష్టించబడింది", "lockdown_initiated": "సిస్టమ్ లాక్‌డౌన్ ప్రారంభించబడింది", "bypass_detected": "భద్రత బైపాస్ గుర్తించబడింది", "section_locked": "విభాగం లాక్ చేయబడింది"},
    "mr": {"name": "Marathi", "alert_prefix": "सुरक्षा चेतावणी", "agent_spawned": "संरक्षण एजंट तयार केला", "lockdown_initiated": "सिस्टम लॉकडाउन सुरू केले", "bypass_detected": "सुरक्षा बायपास आढळला", "section_locked": "विभाग लॉक केला"},
    "ur": {"name": "Urdu", "alert_prefix": "سیکیورٹی انتباہ", "agent_spawned": "دفاعی ایجنٹ تیار کیا گیا", "lockdown_initiated": "سسٹم لاک ڈاؤن شروع کیا گیا", "bypass_detected": "سیکیورٹی بائی پاس کا پتہ چلا", "section_locked": "سیکشن لاک کیا گیا"},
    "sw": {"name": "Swahili", "alert_prefix": "ONYO LA USALAMA", "agent_spawned": "Wakala wa ulinzi ameundwa", "lockdown_initiated": "Kufunga mfumo kumeanzishwa", "bypass_detected": "Kupita usalama kumegunduliwa", "section_locked": "Sehemu imefungwa"},
    "af": {"name": "Afrikaans", "alert_prefix": "SEKURITEITSWAARSḰUWING", "agent_spawned": "Verdedigingsagent geskep", "lockdown_initiated": "Stelsel afsluiting begin", "bypass_detected": "Sekuriteitsomleiding opgespoor", "section_locked": "Afdeling gesluit"},
    "zu": {"name": "Zulu", "alert_prefix": "ISEXWAYISO SOKUPHEPHA", "agent_spawned": "I-agent yokuvikela idalwe", "lockdown_initiated": "Ukuvalwa kwesistimu kuqaliwe", "bypass_detected": "Ukudlula okuphephile kutholiwe", "section_locked": "Isigaba sikhiyiwe"},
    "am": {"name": "Amharic", "alert_prefix": "የደህንነት ማስጠንቀቂያ", "agent_spawned": "የመከላከያ ወኪል ተፈጥሯል", "lockdown_initiated": "የስርዓት መቆለፊያ ተጀምሯል", "bypass_detected": "የደህንነት መዝለል ተገኝቷል", "section_locked": "ክፍል ተቆልፏል"},
    "ne": {"name": "Nepali", "alert_prefix": "सुरक्षा चेतावनी", "agent_spawned": "रक्षा एजेन्ट उत्पन्न भयो", "lockdown_initiated": "प्रणाली लकडाउन सुरु भयो", "bypass_detected": "सुरक्षा बाइपास पत्ता लाग्यो", "section_locked": "खण्ड लक भयो"},
    "si": {"name": "Sinhala", "alert_prefix": "ආරක්ෂක අනතුරු ඇඟවීම", "agent_spawned": "ආරක්ෂක නියෝජිතයා නිර්මාණය කෙරිණි", "lockdown_initiated": "පද්ධති අගුළු දැමීම ආරම්භ කෙරිණි", "bypass_detected": "ආරක්ෂක මඟ හැරීම හඳුනාගෙන ඇත", "section_locked": "කොටස අගුළු දමා ඇත"},
    "km": {"name": "Khmer", "alert_prefix": "ការព្រមានសន្តិសុខ", "agent_spawned": "ភ្នាក់ងារការពារត្រូវបានបង្កើត", "lockdown_initiated": "ការចាក់សោប្រព័ន្ធត្រូវបានផ្តើម", "bypass_detected": "រកឃើញការរំលងសន្តិសុខ", "section_locked": "ផ្នែកត្រូវបានចាក់សោ"},
    "lo": {"name": "Lao", "alert_prefix": "ການເຕືອນຄວາມປອດໄພ", "agent_spawned": "ຕົວແທນປ້ອງກັນຖືກສ້າງຂຶ້ນ", "lockdown_initiated": "ການລັອກລະບົບເລີ່ມຕົ້ນແລ້ວ", "bypass_detected": "ກວດພົບການຂ້າມຄວາມປອດໄພ", "section_locked": "ພາກສ່ວນຖືກລັອກ"},
    "my": {"name": "Burmese", "alert_prefix": "လုံခြုံရေးသတိပေးချက်", "agent_spawned": "ကာကွယ်ရေးအေးဂျင့်ဖန်တီးပြီး", "lockdown_initiated": "စနစ်လော့ခ်ချမှုစတင်ပြီး", "bypass_detected": "လုံခြုံရေးကျော်လွန်မှုတွေ့ရှိပြီး", "section_locked": "အပိုင်းလော့ခ်ချပြီး"},
    "ka": {"name": "Georgian", "alert_prefix": "უსაფრთხოების გაფრთხილება", "agent_spawned": "დამცავი აგენტი შეიქმნა", "lockdown_initiated": "სისტემის ბლოკირება დაწყებულია", "bypass_detected": "უსაფრთხოების გვერდის ავლა აღმოჩენილია", "section_locked": "განყოფილება დაბლოკილია"},
    "hy": {"name": "Armenian", "alert_prefix": "ԱՆՎՏԱՆԳՈՒԹՅԱՆ ԱԶԴԱՆՇԱՆ", "agent_spawned": "Պաշտպանության գործակալ ստեղծված է", "lockdown_initiated": "Համակարգի արգելափակում սկսված է", "bypass_detected": "Անվտանգության շրջանցում հայտնաբերված է", "section_locked": "Բաժին արգելափակված է"},
    "az": {"name": "Azerbaijani", "alert_prefix": "TƏHLÜKƏSİZLİK XƏBƏRDARLIGI", "agent_spawned": "Müdafiə agenti yaradıldı", "lockdown_initiated": "Sistem bağlanması başladıldı", "bypass_detected": "Təhlükəsizlik yan keçməsi aşkar edildi", "section_locked": "Bölmə kilidləndi"},
    "kk": {"name": "Kazakh", "alert_prefix": "ҚАУІПСІЗДІК ЕСКЕРТУІ", "agent_spawned": "Қорғаныс агенті жасалды", "lockdown_initiated": "Жүйе құлыптауы басталды", "bypass_detected": "Қауіпсіздікті айналып өту анықталды", "section_locked": "Бөлім құлыпталды"},
    "uz": {"name": "Uzbek", "alert_prefix": "XAVFSIZLIK OGOHLANTIRISHI", "agent_spawned": "Mudofaa agenti yaratildi", "lockdown_initiated": "Tizim blokirovkasi boshlandi", "bypass_detected": "Xavfsizlik chetlab o'tish aniqlandi", "section_locked": "Bo'lim qulflandi"},
    "mn": {"name": "Mongolian", "alert_prefix": "АЮУЛГҮЙ БАЙДЛЫН АНХААРУУЛГА", "agent_spawned": "Хамгаалалтын төлөөлөгч үүсгэгдсэн", "lockdown_initiated": "Системийн түгжээ эхэлсэн", "bypass_detected": "Аюулгүй байдлын тойрч гарах илрүүлсэн", "section_locked": "Хэсэг түгжигдсэн"}
}

# 50 Programming languages with execution details
PROGRAMMING_LANGUAGES = {
    "python": {"name": "Python", "executable": "python3", "extension": ".py", "installed": True},
    "javascript": {"name": "JavaScript", "executable": "node", "extension": ".js", "installed": True},
    "go": {"name": "Go", "executable": "go", "extension": ".go", "installed": True},
    "rust": {"name": "Rust", "executable": "rustc", "extension": ".rs", "installed": True},
    "java": {"name": "Java", "executable": "java", "extension": ".java", "installed": True},
    "cpp": {"name": "C++", "executable": "g++", "extension": ".cpp", "installed": True},
    "c": {"name": "C", "executable": "gcc", "extension": ".c", "installed": True},
    "ruby": {"name": "Ruby", "executable": "ruby", "extension": ".rb", "installed": True},
    "php": {"name": "PHP", "executable": "php", "extension": ".php", "installed": True},
    "perl": {"name": "Perl", "executable": "perl", "extension": ".pl", "installed": True},
    "csharp": {"name": "C#", "executable": "dotnet", "extension": ".cs", "installed": True},
    "bash": {"name": "Bash", "executable": "bash", "extension": ".sh", "installed": True},
    "typescript": {"name": "TypeScript", "executable": "npx ts-node", "extension": ".ts", "installed": False},
    "kotlin": {"name": "Kotlin", "executable": "kotlin", "extension": ".kt", "installed": False},
    "swift": {"name": "Swift", "executable": "swift", "extension": ".swift", "installed": False},
    "scala": {"name": "Scala", "executable": "scala", "extension": ".scala", "installed": False},
    "lua": {"name": "Lua", "executable": "lua", "extension": ".lua", "installed": False},
    "r": {"name": "R", "executable": "Rscript", "extension": ".R", "installed": False},
    "haskell": {"name": "Haskell", "executable": "runhaskell", "extension": ".hs", "installed": False},
    "elixir": {"name": "Elixir", "executable": "elixir", "extension": ".ex", "installed": False},
    "erlang": {"name": "Erlang", "executable": "erl", "extension": ".erl", "installed": False},
    "clojure": {"name": "Clojure", "executable": "clojure", "extension": ".clj", "installed": False},
    "dart": {"name": "Dart", "executable": "dart", "extension": ".dart", "installed": False},
    "groovy": {"name": "Groovy", "executable": "groovy", "extension": ".groovy", "installed": False},
    "julia": {"name": "Julia", "executable": "julia", "extension": ".jl", "installed": False},
    "fsharp": {"name": "F#", "executable": "dotnet fsi", "extension": ".fs", "installed": True},
    "ocaml": {"name": "OCaml", "executable": "ocaml", "extension": ".ml", "installed": False},
    "nim": {"name": "Nim", "executable": "nim", "extension": ".nim", "installed": False},
    "crystal": {"name": "Crystal", "executable": "crystal", "extension": ".cr", "installed": False},
    "zig": {"name": "Zig", "executable": "zig", "extension": ".zig", "installed": False},
    "d": {"name": "D", "executable": "dmd", "extension": ".d", "installed": False},
    "fortran": {"name": "Fortran", "executable": "gfortran", "extension": ".f90", "installed": False},
    "cobol": {"name": "COBOL", "executable": "cobc", "extension": ".cob", "installed": False},
    "ada": {"name": "Ada", "executable": "gnatmake", "extension": ".adb", "installed": False},
    "pascal": {"name": "Pascal", "executable": "fpc", "extension": ".pas", "installed": False},
    "lisp": {"name": "Common Lisp", "executable": "sbcl", "extension": ".lisp", "installed": False},
    "scheme": {"name": "Scheme", "executable": "guile", "extension": ".scm", "installed": False},
    "prolog": {"name": "Prolog", "executable": "swipl", "extension": ".pl", "installed": False},
    "racket": {"name": "Racket", "executable": "racket", "extension": ".rkt", "installed": False},
    "tcl": {"name": "Tcl", "executable": "tclsh", "extension": ".tcl", "installed": False},
    "vb": {"name": "Visual Basic", "executable": "dotnet", "extension": ".vb", "installed": True},
    "smalltalk": {"name": "Smalltalk", "executable": "gst", "extension": ".st", "installed": False},
    "powershell": {"name": "PowerShell", "executable": "pwsh", "extension": ".ps1", "installed": False},
    "assembly": {"name": "Assembly", "executable": "nasm", "extension": ".asm", "installed": False},
    "v": {"name": "V", "executable": "v", "extension": ".v", "installed": False},
    "hack": {"name": "Hack", "executable": "hhvm", "extension": ".hack", "installed": False},
    "objectivec": {"name": "Objective-C", "executable": "gcc", "extension": ".m", "installed": True},
    "vhdl": {"name": "VHDL", "executable": "ghdl", "extension": ".vhdl", "installed": False},
    "verilog": {"name": "Verilog", "executable": "iverilog", "extension": ".v", "installed": False},
    "solidity": {"name": "Solidity", "executable": "solc", "extension": ".sol", "installed": False}
}


def generate_language_database():
    """Generate comprehensive language database."""
    data = {
        "human_languages": HUMAN_LANGUAGES,
        "programming_languages": PROGRAMMING_LANGUAGES,
        "metadata": {
            "total_human_languages": len(HUMAN_LANGUAGES),
            "total_programming_languages": len(PROGRAMMING_LANGUAGES),
            "created": "2026-01-23",
            "purpose": "Cerberus Hydra Defense Mechanism - Multi-language agent spawning"
        }
    }
    
    output_path = Path(__file__).parent.parent / "data" / "cerberus" / "languages.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated language database: {output_path}")
    print(f"  - {len(HUMAN_LANGUAGES)} human languages")
    print(f"  - {len(PROGRAMMING_LANGUAGES)} programming languages")
    
    return output_path


if __name__ == "__main__":
    generate_language_database()
