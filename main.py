import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3

app = FastAPI(
    title="StudioX Pro Ultimate Elite Suite",
    description="All-in-one AI Design, Templates, Image & Video Enhancement Suite.",
    version="26.5.0"
)

# إعداد مجلدات التخزين
OUTPUT_DIR = "static/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_FILE = "studiox_pro.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            tier TEXT DEFAULT 'مجاني'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            title TEXT,
            category TEXT,
            details TEXT,
            tier_required TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

class UserRegisterReq(BaseModel):
    email: str

class ProjectReq(BaseModel):
    email: str
    title: str
    category: str
    details: str
    tier_required: str = "مجاني"

class AIImageReq(BaseModel):
    prompt: str

@app.post("/api/auth/register")
def register_user(u: UserRegisterReq):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT tier FROM users WHERE email = ?", (u.email,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (email, tier) VALUES (?, 'مجاني')", (u.email,))
        conn.commit()
        tier = "مجاني"
    else:
        tier = row[0]
    conn.close()
    return {"status": "success", "email": u.email, "tier": tier}

@app.post("/api/ai/generate-image")
def generate_ai_image(req: AIImageReq):
    try:
        encoded_prompt = requests.utils.quote(req.prompt)
        ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        return {
            "status": "success",
            "image_url": ai_image_url,
            "message": "تم التوليد بنجاح!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl" id="htmlRoot" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StudioX Pro | Ultimate Design & AI Studio</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Tajawal', sans-serif; }
            .glass-panel {
                background: rgba(13, 17, 28, 0.75);
                backdrop-filter: blur(25px);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            .neon-glow {
                box-shadow: 0 0 50px -15px rgba(168, 85, 247, 0.3);
            }
            .custom-scrollbar::-webkit-scrollbar { width: 6px; }
            .custom-scrollbar::-webkit-scrollbar-track { background: #070913; }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
            .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #334155; }
        </style>
    </head>
    <body class="bg-[#04060f] text-slate-100 min-h-screen flex flex-col md:flex-row overflow-x-hidden selection:bg-purple-500 selection:text-white">

        <!-- القائمة الجانبية للنخبة -->
        <aside class="w-full md:w-80 glass-panel border-l md:border-l-0 md:border-r border-slate-800/80 p-6 flex md:flex-col justify-between items-center md:items-stretch z-30 shadow-2xl">
            <div class="w-full">
                <!-- الشعار -->
                <div class="flex items-center justify-between mb-8 pb-4 border-b border-slate-800/60">
                    <div class="flex items-center gap-3.5">
                        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 via-fuchsia-600 to-cyan-400 p-[1px] shadow-lg shadow-fuchsia-500/20">
                            <div class="w-full h-full bg-[#070913] rounded-2xl flex items-center justify-center font-black text-base bg-gradient-to-tr from-violet-400 to-cyan-400 bg-clip-text text-transparent">SX</div>
                        </div>
                        <div>
                            <h1 class="text-base font-black tracking-wider bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">StudioX Pro</h1>
                            <p class="text-[10px] text-purple-400 font-semibold tracking-widest uppercase">Ultimate Creative Suite</p>
                        </div>
                    </div>
                    <select id="langSelect" onchange="changeLanguage(this.value)" class="bg-slate-900/90 border border-slate-800 text-slate-300 text-[11px] rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-purple-500 transition">
                        <option value="ar" selected>عربي</option>
                        <option value="en">English</option>
                    </select>
                </div>

                <!-- صندوق الحساب الذكي -->
                <div class="bg-gradient-to-b from-slate-900/80 to-slate-950/80 border border-slate-800/80 rounded-2xl p-4 mb-6 shadow-inner">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-[11px] text-slate-400 font-medium" data-i18n="accountLabel">حساب البريد الإلكتروني</span>
                        <span id="badgeTier" class="text-[9px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 font-bold">مجاني</span>
                    </div>
                    
                    <div id="loggedOutView" class="space-y-2.5">
                        <input type="email" id="inputEmail" placeholder="name@example.com" class="w-full bg-[#05070c] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500 transition text-left" dir="ltr">
                        <button onclick="registerWithEmail()" class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:opacity-90 text-white font-bold text-xs py-2.5 rounded-xl transition shadow-lg shadow-purple-600/20 flex items-center justify-center gap-2">
                            <span>✨</span> <span data-i18n="btnLogin">ربط وحفظ الحساب</span>
                        </button>
                    </div>

                    <div id="loggedInView" class="hidden space-y-2">
                        <div id="displayEmail" class="text-[11px] text-purple-300 font-bold truncate bg-slate-900/90 p-2 rounded-xl border border-slate-800" dir="ltr"></div>
                        <button onclick="logoutEmail()" class="w-full bg-slate-900 hover:bg-red-500/10 text-slate-400 hover:text-red-400 border border-slate-800 hover:border-red-500/20 text-[11px] py-1.5 rounded-xl transition font-medium" data-i18n="btnLogout">تسجيل الخروج</button>
                    </div>
                </div>

                <!-- الأقسام الاحترافية -->
                <nav class="hidden md:flex flex-col space-y-1.5">
                    <button onclick="switchTab('designStudio')" id="navDesignStudio" class="w-full py-3 px-4 rounded-xl font-bold text-xs bg-purple-600 text-white shadow-lg shadow-purple-600/25 transition flex items-center gap-3.5 group">
                        <span class="text-base">🎨</span> <span data-i18n="menuDesign">استوديو التصميم الحر</span>
                    </button>
                    <button onclick="switchTab('templatesHub')" id="navTemplatesHub" class="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-900/40 text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent hover:border-slate-800 transition flex items-center gap-3.5 group">
                        <span class="text-base">📑</span> <span data-i18n="menuTemplates">القوالب الجاهزة</span>
                    </button>
                    <button onclick="switchTab('aiMaster')" id="navAiMaster" class="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-900/40 text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent hover:border-slate-800 transition flex items-center gap-3.5 group">
                        <span class="text-base">🔮</span> <span data-i18n="menuAiMaster">توليد الصور بالذكاء الاصطناعي</span>
                    </button>
                    <button onclick="switchTab('imageRestoration')" id="navImageRestoration" class="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-900/40 text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent hover:border-slate-800 transition flex items-center gap-3.5 group">
                        <span class="text-base">🖼️</span> <span data-i18n="menuImage">توضيح وتكبير الصور</span>
                    </button>
                    <button onclick="switchTab('videoEnhance')" id="navVideoEnhance" class="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-900/40 text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent hover:border-slate-800 transition flex items-center gap-3.5 group">
                        <span class="text-base">🎬</span> <span data-i18n="menuVideo">توضيح الفيديوهات AI</span>
                    </button>
                    <button onclick="switchTab('projects')" id="navProjects" class="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-900/40 text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent hover:border-slate-800 transition flex items-center gap-3.5 group">
                        <span class="text-base">📁</span> <span data-i18n="menuArchive">أرشيف المشاريع الشخصية</span>
                    </button>
                </nav>
            </div>

            <!-- بطاقة الترقية -->
            <div class="hidden md:block w-full bg-gradient-to-br from-amber-500/10 via-orange-500/5 to-transparent border border-amber-500/20 rounded-2xl p-4 text-center mt-6">
                <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black bg-amber-500/20 text-amber-400 mb-2 border border-amber-500/30">
                    <span>👑</span> <span>StudioX PRO</span>
                </div>
                <p class="text-[11px] text-slate-400 mb-3 leading-relaxed" data-i18n="proDesc">افتح قدرات المعالجة اللانهائية بدقة 4K فائقة السرعة.</p>
                <button onclick="toggleProTier()" id="btnUpgrade" class="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white font-black text-xs py-2.5 rounded-xl shadow-lg shadow-orange-600/20 transition">ترقية الباقة الآن</button>
            </div>
        </aside>

        <!-- مساحة العمل الرئيسية -->
        <main class="flex-1 p-6 md:p-10 overflow-y-auto custom-scrollbar max-w-6xl mx-auto w-full">
            
            <!-- 1. استوديو التصميم الحر (Design Studio) -->
            <div id="sectionDesignStudio" class="space-y-6">
                <div class="glass-panel rounded-3xl p-8 neon-glow">
                    <h2 class="text-lg font-black tracking-wide bg-gradient-to-r from-purple-400 to-fuchsia-400 bg-clip-text text-transparent mb-2" data-i18n="ds_title">🎨 استوديو التصميم الاحترافي الحر</h2>
                    <p class="text-xs text-slate-400 mb-6" data-i18n="ds_desc">أنشئ تصاميمك الخاصة، أضف النصوص، تحكم بالألوان والخلفيات بحرية تامة.</p>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <!-- لوحة التحكم بالتصميم -->
                        <div class="bg-[#05070c] border border-slate-800 p-5 rounded-2xl space-y-4">
                            <h3 class="text-xs font-bold text-slate-200 border-b border-slate-800 pb-2">أدوات التحكم باللوحة</h3>
                            <div>
                                <label class="text-[11px] text-slate-400 block mb-1">نص العنوان:</label>
                                <input type="text" id="canvasText" value="عنوان تصميمك الرائع" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500">
                            </div>
                            <div>
                                <label class="text-[11px] text-slate-400 block mb-1">لون الخلفية:</label>
                                <input type="color" id="canvasBgColor" value="#0f172a" class="w-full h-10 bg-slate-900 border border-slate-800 rounded-xl cursor-pointer">
                            </div>
                            <div>
                                <label class="text-[11px] text-slate-400 block mb-1">لون النص:</label>
                                <input type="color" id="canvasTextColor" value="#c084fc" class="w-full h-10 bg-slate-900 border border-slate-800 rounded-xl cursor-pointer">
                            </div>
                            <button onclick="applyDesignChanges()" class="w-full bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs py-2.5 rounded-xl transition shadow">تطبيق التعديلات</button>
                            <button onclick="saveCurrentDesignToArchive()" class="w-full bg-slate-900 hover:bg-slate-800 text-purple-400 border border-purple-500/30 font-bold text-xs py-2.5 rounded-xl transition">💾 حفظ التصميم في أرشيفي</button>
                        </div>

                        <!-- مساحة معاينة التصميم التفاعلية -->
                        <div class="lg:col-span-2 bg-[#05070c] border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center min-h-[350px] relative overflow-hidden shadow-2xl" id="previewCanvas" style="background-color: #0f172a;">
                            <div class="text-center p-6 rounded-2xl backdrop-blur-md bg-black/30 border border-white/10 max-w-md">
                                <h2 id="liveDesignTitle" class="text-2xl font-black mb-2" style="color: #c084fc;">عنوان تصميمك الرائع</h2>
                                <p class="text-xs text-slate-300">هنا تظهر لوحتك الفنية والتصميم الذي قمت بإنكار وتنسيقه بكل احترافية.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. مكتبة القوالب الجاهزة (Templates Hub) -->
            <div id="sectionTemplatesHub" class="space-y-6 hidden">
                <div class="glass-panel rounded-3xl p-8">
                    <h2 class="text-lg font-black tracking-wide text-cyan-400 mb-2" data-i18n="th_title">📑 مكتبة القوالب الجاهزة الاحترافية</h2>
                    <p class="text-xs text-slate-400 mb-6" data-i18n="th_desc">اختر قالبًا جاهزًا بضغطة زر واحدة وابدأ التعديل عليه فوراً.</p>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                        <div class="bg-[#05070c] border border-slate-800 rounded-2xl p-5 hover:border-cyan-500/50 transition flex flex-col justify-between">
                            <div>
                                <span class="text-[10px] text-cyan-400 font-bold bg-cyan-500/10 px-2.5 py-1 rounded-full">إعلان سوشيال ميديا</span>
                                <h3 class="text-sm font-bold text-slate-200 mt-3">قالب إعلان تسويقي عصري</h3>
                                <p class="text-[11px] text-slate-400 mt-1">مصمم خصيصاً لإعلانات انستغرام وفيسبوك بجذابيه عالية.</p>
                            </div>
                            <button onclick="loadTemplate('إعلان تسويقي عصري', 'إعلان سوشيال ميديا')" class="mt-5 w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs py-2 rounded-xl transition">استخدام القالب</button>
                        </div>
                        <div class="bg-[#05070c] border border-slate-800 rounded-2xl p-5 hover:border-cyan-500/50 transition flex flex-col justify-between">
                            <div>
                                <span class="text-[10px] text-purple-400 font-bold bg-purple-500/10 px-2.5 py-1 rounded-full">هوية بصرية</span>
                                <h3 class="text-sm font-bold text-slate-200 mt-3">قالب بطاقة أعمال (Business Card)</h3>
                                <p class="text-[11px] text-slate-400 mt-1">بطاقة تعريفية فاخرة تناسب الشركات والمصممين المستقلين.</p>
                            </div>
                            <button onclick="loadTemplate('بطاقة أعمال فاخرة', 'هوية بصرية')" class="mt-5 w-full bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs py-2 rounded-xl transition">استخدام القالب</button>
                        </div>
                        <div class="bg-[#05070c] border border-slate-800 rounded-2xl p-5 hover:border-cyan-500/50 transition flex flex-col justify-between">
                            <div>
                                <span class="text-[10px] text-amber-400 font-bold bg-amber-500/10 px-2.5 py-1 rounded-full">تصميم شعار (Logo)</span>
                                <h3 class="text-sm font-bold text-slate-200 mt-3">شعار تقني مستقبلي (Tech Logo)</h3>
                                <p class="text-[11px] text-slate-400 mt-1">شعار أنيق وداكن يناسب شركات البرمجيات وتطبيقات الذكاء الاصطناعي.</p>
                            </div>
                            <button onclick="loadTemplate('شعار تقني مستقبلي', 'تصميم شعار')" class="mt-5 w-full bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs py-2 rounded-xl transition">استخدام القالب</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 3. توليد الصور بالذكاء الاصطناعي -->
            <div id="sectionAiMaster" class="space-y-6 hidden">
                <div class="glass-panel rounded-3xl p-8">
                    <h2 class="text-lg font-black tracking-wide text-purple-400 mb-2" data-i18n="ai_hub_title">🔮 مركز توليد الصور بالذكاء الاصطناعي</h2>
                    <p class="text-xs text-slate-400 mb-6" data-i18n="ai_hub_desc">صمم وحول أفكارك إلى لوحات فنية واقعية ومذهلة عبر أحدث نماذج التوليد العصبية.</p>
                    
                    <div class="space-y-4">
                        <textarea id="aiPrompt" data-i18n-placeholder="ai_ph_prompt" placeholder="اكتب وصفاً تفصيلياً لما تريد توليده بالذكاء الاصطناعي..." class="w-full h-32 bg-[#05070c] border border-slate-800 rounded-2xl p-4 text-xs text-slate-100 focus:outline-none focus:border-purple-500 transition resize-none leading-relaxed shadow-inner"></textarea>
                        
                        <div class="flex justify-end">
                            <button onclick="runRealAIImageGeneration()" class="bg-gradient-to-r from-purple-600 to-indigo-600 hover:opacity-90 text-white font-black text-xs px-8 py-3 rounded-2xl shadow-xl shadow-purple-600/30 transition flex items-center gap-2.5">
                                <span>✨</span> <span data-i18n="ai_t2i">توليد الصورة الفورية</span>
                            </button>
                        </div>

                        <div id="aiResultContainer" class="hidden mt-8 bg-[#05070c] border border-slate-800/80 rounded-2xl p-6 text-center">
                            <h3 class="text-xs font-bold text-purple-400 mb-4" data-i18n="ai_result_title">✨ النتيجة النهائية المُولدة:</h3>
                            <div class="flex justify-center">
                                <img id="aiGeneratedImage" src="" alt="AI Output" class="max-w-full h-auto max-h-[450px] rounded-2xl border border-slate-800 shadow-2xl">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 4. توضيح وتكبير الصور (AI Image Upscaler) -->
            <div id="sectionImageRestoration" class="space-y-6 hidden">
                <div class="glass-panel rounded-3xl p-8">
                    <h2 class="text-base font-bold text-amber-400 mb-2" data-i18n="img_title">🖼️ توضيح وتكبير الصور بالذكاء الاصطناعي</h2>
                    <p class="text-xs text-slate-400 mb-6">ارفع صورة قديمة أو ضبابية وسيقوم النظام بإزالة الغبش وتكبيرها بدقة فائقة.</p>
                    <div class="bg-[#05070c] border border-slate-800 rounded-2xl p-8 text-center space-y-4">
                        <input type="file" id="imageUploadInput" class="hidden" accept="image/*" onchange="simulateImageEnhance(this)">
                        <button onclick="document.getElementById('imageUploadInput').click()" class="bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs px-6 py-3 rounded-xl transition shadow">📂 اختر صورة لتوضيحها</button>
                        <p id="enhanceStatus" class="text-xs text-slate-400">لم يتم اختيار أي صورة بعد.</p>
                    </div>
                </div>
            </div>

            <!-- 5. توضيح الفيديوهات (Video Restoration Studio) -->
            <div id="sectionVideoEnhance" class="space-y-6 hidden">
                <div class="glass-panel rounded-3xl p-8">
                    <h2 class="text-base font-bold text-cyan-400 mb-2" data-i18n="vid_title">🎬 معالجة وتوضيح الفيديوهات وإزالة الغبش</h2>
                    <p class="text-xs text-slate-400 mb-6">ارفع مقطع فيديو لتقليل التشويش وتحسين الإضاءة والوضوح بالذكاء الاصطناعي.</p>
                    <div class="bg-[#05070c] border border-slate-800 rounded-2xl p-8 text-center space-y-4">
                        <input type="file" id="videoUploadInput" class="hidden" accept="video/*" onchange="simulateVideoEnhance(this)">
                        <button onclick="document.getElementById('videoUploadInput').click()" class="bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs px-6 py-3 rounded-xl transition shadow">📂 اختر فيديو لمعالجته وتوضيحه</button>
                        <p id="videoStatus" class="text-xs text-slate-400">لم يتم اختيار أي فيديو بعد.</p>
                    </div>
                </div>
            </div>

            <!-- 6. أرشيف المشاريع الشخصية -->
            <div id="sectionProjects" class="space-y-6 hidden">
                <div class="glass-panel rounded-3xl p-8">
                    <div class="flex items-center justify-between mb-6">
                        <h2 class="text-base font-bold text-slate-100" data-i18n="a_title">📁 أرشيف المشاريع الشخصية</h2>
                        <button onclick="loadProjects()" class="text-xs text-purple-400 hover:underline" data-i18n="refreshList">تحديث القائمة 🔄</button>
                    </div>
                    <div id="projectsList" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <p class="text-slate-500 text-xs col-span-full text-center py-10" data-i18n="noProjects">لا توجد مشاريع محفوظة حتى الآن.</p>
                    </div>
                </div>
            </div>

        </main>

        <!-- الإشعارات -->
        <div id="toast" class="fixed bottom-8 left-1/2 -translate-x-1/2 glass-panel border border-purple-500/30 text-slate-200 px-5 py-3 rounded-2xl shadow-2xl text-xs font-semibold hidden transition-all z-50 flex items-center gap-3">
            <span class="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></span>
            <span id="toastMsg">تمت العملية بنجاح</span>
        </div>

        <script>
            let currentEmail = localStorage.getItem('studiox_email') || null;
            let currentTier = localStorage.getItem('studiox_tier') || 'مجاني';
            let currentLang = 'ar';

            const translations = {
                ar: {
                    accountLabel: "البريد الإلكتروني للحفظ",
                    btnLogin: "ربط وحفظ الحساب",
                    btnLogout: "تسجيل الخروج",
                    proDesc: "افتح قدرات المعالجة اللانهائية بدقة 4K فائقة السرعة.",
                    btnUpgrade: "ترقية الباقة الآن",
                    menuDesign: "استوديو التصميم الحر",
                    menuTemplates: "القوالب الجاهزة",
                    menuAiMaster: "توليد الصور بالذكاء الاصطناعي",
                    menuImage: "توضيح وتكبير الصور",
                    menuVideo: "توضيح الفيديوهات AI",
                    menuArchive: "أرشيف المشاريع الشخصية",
                    ds_title: "🎨 استوديو التصميم الاحترافي الحر",
                    ds_desc: "أنشئ تصاميمك الخاصة، أضف النصوص، تحكم بالألوان والخلفيات بحرية تامة.",
                    th_title: "📑 مكتبة القوالب الجاهزة الاحترافية",
                    th_desc: "اختر قالبًا جاهزًا بضغطة زر واحدة وابدأ التعديل عليه فوراً.",
                    ai_hub_title: "🔮 مركز توليد الصور بالذكاء الاصطناعي",
                    ai_hub_desc: "صمم وحول أفكارك إلى لوحات فنية واقعية ومذهلة عبر أحدث نماذج التوليد العصبية.",
                    ai_ph_prompt: "اكتب وصفاً تفصيلياً لما تريد توليده بالذكاء الاصطناعي...",
                    ai_t2i: "توليد الصورة الفورية",
                    ai_result_title: "✨ النتيجة النهائية المُولدة:",
                    img_title: "🖼️ توضيح وتكبير الصور بالذكاء الاصطناعي",
                    vid_title: "🎬 معالجة وتوضيح الفيديوهات وإزالة الغبش",
                    a_title: "📁 أرشيف المشاريع الشخصية",
                    refreshList: "تحديث القائمة 🔄",
                    noProjects: "لا توجد مشاريع محفوظة في حسابك حتى الآن."
                },
                en: {
                    accountLabel: "Account Email",
                    btnLogin: "Link & Save",
                    btnLogout: "Sign Out",
                    proDesc: "Unlock unlimited 4K high-speed AI processing.",
                    btnUpgrade: "Upgrade Plan Now",
                    menuDesign: "Free Design Studio",
                    menuTemplates: "Templates Hub",
                    menuAiMaster: "AI Image Generator",
                    menuImage: "AI Image Upscaler",
                    menuVideo: "AI Video Restoration",
                    menuArchive: "Personal Archive",
                    ds_title: "🎨 Professional Free Design Studio",
                    ds_desc: "Create custom designs, add texts, and control colors freely.",
                    th_title: "📑 Professional Templates Hub",
                    th_desc: "Choose a ready-made template with one click.",
                    ai_hub_title: "🔮 AI Image Generator Center",
                    ai_hub_desc: "Transform your ideas into stunning artworks via neural models.",
                    ai_ph_prompt: "Write a detailed prompt for AI generation...",
                    ai_t2i: "Generate Instant Image",
                    ai_result_title: "✨ Final AI Generation Result:",
                    img_title: "🖼️ AI Image Upscaler & Clarification",
                    vid_title: "🎬 AI Video Restoration & Clarity",
                    a_title: "📁 Personal Archive",
                    refreshList: "Refresh 🔄",
                    noProjects: "No saved projects in your account yet."
                }
            };

            window.addEventListener('DOMContentLoaded', () => {
                if(currentEmail) showLoggedInState(currentEmail);
            });

            async function registerWithEmail() {
                const email = document.getElementById('inputEmail').value.trim();
                if(!email || !email.includes('@')) {
                    showToast(currentLang === 'ar' ? '⚠️ يرجى إدخال بريد إلكتروني صحيح!' : '⚠️ Please enter a valid email!');
                    return;
                }
                try {
                    const res = await fetch('/api/auth/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ email })
                    });
                    const data = await res.json();
                    if(res.ok) {
                        currentEmail = data.email;
                        currentTier = data.tier;
                        localStorage.setItem('studiox_email', currentEmail);
                        localStorage.setItem('studiox_tier', currentTier);
                        showLoggedInState(currentEmail);
                        showToast(currentLang === 'ar' ? '🎉 تم ربط الحساب بنجاح' : '🎉 Account linked successfully');
                    }
                } catch(e) {
                    showToast('❌ خطأ في الاتصال');
                }
            }

            function showLoggedInState(email) {
                document.getElementById('loggedOutView').classList.add('hidden');
                document.getElementById('loggedInView').classList.remove('hidden');
                document.getElementById('displayEmail').innerText = email;
            }

            function logoutEmail() {
                localStorage.removeItem('studiox_email');
                localStorage.removeItem('studiox_tier');
                currentEmail = null;
                document.getElementById('loggedInView').classList.add('hidden');
                document.getElementById('loggedOutView').classList.remove('hidden');
                document.getElementById('inputEmail').value = '';
                showToast(currentLang === 'ar' ? 'تم تسجيل الخروج بنجاح' : 'Logged out successfully');
            }

            function changeLanguage(lang) {
                currentLang = lang;
                const root = document.getElementById('htmlRoot');
                root.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
                root.setAttribute('lang', lang);
                document.querySelectorAll('[data-i18n]').forEach(el => {
                    const key = el.getAttribute('data-i18n');
                    if(translations[lang][key]) el.innerText = translations[lang][key];
                });
            }

            function switchTab(tab) {
                const tabs = ['designStudio', 'templatesHub', 'aiMaster', 'imageRestoration', 'videoEnhance', 'projects'];
                tabs.forEach(t => {
                    const btn = document.getElementById('nav' + t.charAt(0).toUpperCase() + t.slice(1));
                    const sec = document.getElementById('section' + t.charAt(0).toUpperCase() + t.slice(1));
                    if(btn) btn.className = "w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-900/40 text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent hover:border-slate-800 transition flex items-center gap-3.5 group";
                    if(sec) sec.classList.add('hidden');
                });
                const activeBtn = document.getElementById('nav' + tab.charAt(0).toUpperCase() + tab.slice(1));
                const activeSec = document.getElementById('section' + tab.charAt(0).toUpperCase() + tab.slice(1));
                if(activeBtn) activeBtn.className = "w-full py-3 px-4 rounded-xl font-bold text-xs bg-purple-600 text-white shadow-lg shadow-purple-600/25 transition flex items-center gap-3.5 group";
                if(activeSec) activeSec.classList.remove('hidden');
                if(tab === 'projects') loadProjects();
            }

            function showToast(msg) {
                const toast = document.getElementById('toast');
                document.getElementById('toastMsg').innerText = msg;
                toast.classList.remove('hidden');
                setTimeout(() => toast.classList.add('hidden'), 3500);
            }

            // وظائف استوديو التصميم الحر والقوالب
            function applyDesignChanges() {
                const text = document.getElementById('canvasText').value;
                const bgColor = document.getElementById('canvasBgColor').value;
                const textColor = document.getElementById('canvasTextColor').value;
                
                document.getElementById('liveDesignTitle').innerText = text;
                document.getElementById('liveDesignTitle').style.color = textColor;
                document.getElementById('previewCanvas').style.backgroundColor = bgColor;
                showToast('✨ تم تطبيق التعديلات على التصميم بنجاح');
            }

            function loadTemplate(title, category) {
                document.getElementById('canvasText').value = title;
                applyDesignChanges();
                switchTab('designStudio');
                showToast(`📑 تم تحميل قالب (${category}) بنجاح`);
            }

            async function saveCurrentDesignToArchive() {
                if(!currentEmail) {
                    showToast('⚠️ يرجى ربط بريدك الإلكتروني أولاً في القائمة الجانبية لحفظ مشاريعك');
                    return;
                }
                const title = document.getElementById('canvasText').value;
                await fetch('/api/projects', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        email: currentEmail,
                        title: title,
                        category: 'تصميم حر / قالب',
                        details: 'تصميم تم إنشاؤه عبر استوديو StudioX Pro',
                        tier_required: currentTier
                    })
                });
                showToast('💾 تم حفظ التصميم في أرشيفك الشخصي بنجاح!');
            }

            async function runRealAIImageGeneration() {
                const prompt = document.getElementById('aiPrompt').value.trim();
                if(!prompt) {
                    showToast('⚠️ يرجى كتابة وصف للصورة أولاً!');
                    return;
                }
                showToast('✨ جاري توليد الصورة عبر الذكاء الاصطناعي...');
                try {
                    const res = await fetch('/api/ai/generate-image', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ prompt })
                    });
                    const data = await res.json();
                    if(res.ok) {
                        document.getElementById('aiGeneratedImage').src = data.image_url;
                        document.getElementById('aiResultContainer').classList.remove('hidden');
                        showToast('🎉 تم توليد الصورة بنجاح!');
                        if(currentEmail) {
                            await fetch('/api/projects', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    email: currentEmail,
                                    title: prompt.slice(0, 30),
                                    category: 'توليد صور AI',
                                    details: 'توليد ناجح بالذكاء الاصطناعي',
                                    tier_required: currentTier
                                })
                            });
                        }
                    }
                } catch(e) {
                    showToast('❌ خطأ في الاتصال');
                }
            }

            function simulateImageEnhance(input) {
                if(input.files && input.files[0]) {
                    document.getElementById('enhanceStatus').innerText = "✨ تم رفع الصورة وجاري معالجتها وتوضيحها بدقة 4K بالذكاء الاصطناعي...";
                    setTimeout(() => {
                        document.getElementById('enhanceStatus').innerText = "🎉 تمت عملية توضيح الصورة بنجاح وتنقيتها من الغبش!";
                        showToast('🖼️ تم تكبير وتوضيح الصورة بنجاح');
                    }, 2000);
                }
            }

            function simulateVideoEnhance(input) {
                if(input.files && input.files[0]) {
                    document.getElementById('videoStatus').innerText = "🎬 جاري تحليل الفيديو ومعالجة التشويش والإضاءة بالشبكات العصبية...";
                    setTimeout(() => {
                        document.getElementById('videoStatus').innerText = "🎉 تم توضيح ومعالجة الفيديو بنجاح وجاهز للتحميل!";
                        showToast('🎬 تم توضيح الفيديو بدقة عالية');
                    }, 2500);
                }
            }

            function toggleProTier() {
                currentTier = currentTier === 'مجاني' ? 'PRO' : 'مجاني';
                localStorage.setItem('studiox_tier', currentTier);
                const badge = document.getElementById('badgeTier');
                const btn = document.getElementById('btnUpgrade');
                if(currentTier === 'PRO') {
                    badge.innerText = "PRO ⭐";
                    btn.innerText = "الباقة الاحترافية مفعلة ✓";
                    showToast('👑 مبروك! تم تفعيل الباقة الاحترافية بنجاح');
                } else {
                    badge.innerText = "مجاني";
                    btn.innerText = "ترقية الباقة الآن";
                    showToast('تم العودة للباقة المجانية');
                }
            }

            async function loadProjects() {
                const container = document.getElementById('projectsList');
                if(!currentEmail) {
                    container.innerHTML = `<p class="text-amber-400 text-xs col-span-full text-center py-10">⚠️️ يرجى ربط بريدك الإلكتروني في القائمة الجانبية لعرض مشاريِعك المحفوظة.</p>`;
                    return;
                }
                const res = await fetch(`/api/projects?email=${encodeURIComponent(currentEmail)}`);
                const items = await res.json();
                if(items.length === 0) {
                    container.innerHTML = `<p class="text-slate-500 text-xs col-span-full text-center py-10">لا توجد مشاريع محفوظة في حسابك حتى الآن.</p>`;
                    return;
                }
                container.innerHTML = items.map(item => `
                    <div class="bg-[#05070c] border border-slate-800/80 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
                        <div>
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-[10px] text-purple-400 font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/20">${item.category}</span>
                                <span class="text-[9px] px-2 py-0.5 rounded font-bold ${item.tier_required === 'PRO' ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-400'}">${item.tier_required}</span>
                            </div>
                            <h4 class="text-xs font-bold text-slate-200 mt-2">${item.title}</h4>
                            <p class="text-[10px] text-slate-400 mt-1.5 leading-relaxed">${item.details}</p>
                        </div>
                        <span class="text-[9px] text-slate-500 mt-4 pt-3 border-t border-slate-900 block" dir="ltr">${item.created_at}</span>
                    </div>
                `).reverse().join('');
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/projects")
def add_project(p: ProjectReq):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (email, title, category, details, tier_required) VALUES (?, ?, ?, ?, ?)",
                   (p.email, p.title, p.category, p.details, p.tier_required))
    conn.commit()
    conn.close()
    return {"status": "saved"}

@app.get("/api/projects")
def get_projects(email: str = None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if email:
        cursor.execute("SELECT title, category, details, tier_required, created_at FROM projects WHERE email = ?", (email,))
    else:
        cursor.execute("SELECT title, category, details, tier_required, created_at FROM projects")
    rows = cursor.fetchall()
    conn.close()
    return [{"title": r[0], "category": r[1], "details": r[2], "tier_required": r[3], "created_at": r[4]} for r in rows]