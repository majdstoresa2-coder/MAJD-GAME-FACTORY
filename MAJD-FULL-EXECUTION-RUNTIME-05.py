name: MAJD Game Factory Web Test  
  
on:  
  workflow_dispatch:  
    inputs:  
      owner_command:  
        description: 'أمر المالك (Owner Command) - العقل المدبر سيتولى تنفيذه'  
        required: false  
        default: 'أنشئ لعبة حقيقية كاملة واختبرها وأصلح الأخطاء تلقائياً وجهز النسخة القابلة للعب'  
  
jobs:  
  web-build-test:  
    runs-on: ubuntu-latest  
    permissions:  
      contents: read  
      actions: write  
    steps:  
      # 1. تحميل المستودع  
      - name: Checkout Repository  
        uses: actions/checkout@v4  
  
      # 2. إعداد بيئة بايثون (ضروري جداً)  
      - name: Set up Python  
        uses: actions/setup-python@v5  
        with:  
          python-version: '3.10'  
  
      # 3. تثبيت المكتبات التي تحتاجها ملفات 01, 03, 04  
      # (هذا الشرط ضروري لتجنب فشل التشغيل. سيتم تفعيله عند الحاجة)  
      - name: Install Python Dependencies  
        run: |  
          echo "جارٍ تثبيت المكتبات الأساسية (موجودة بالتعليق)."  
          # pip install openai requests  # <--- إذا ظهر خطأ ModuleNotFoundError، أزل التعليق واكتب اسم المكتبة هنا  
  
      # 4. تشغيل الملف التشغيلي الرئيسي (05) الذي يربط 01 و 02 و 03 و 04  
      - name: Execute MAJD Full Factory Runtime  
        # يتم تمرير الأمر كوسيط (arg) ليستقبله 05.py عبر sys.argv  
        run: python MAJD-FULL-EXECUTION-RUNTIME-05.py "${{ github.event.inputs.owner_command }}"  
  
      # 5. رفع النتائج النهائية (اللعبة القابلة للعب) للمراجعة  
      - name: Upload Playable Game Artifact  
        if: success() || failure()  
        uses: actions/upload-artifact@v4  
        with:  
          name: majd-game-final-output  
          path: |  
            majd_game_output/  
            majd_factory_state/runtime/  
