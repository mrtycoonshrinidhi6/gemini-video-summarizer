Write-Host "🚀 Starting MoviePy Fix Script..." -ForegroundColor Cyan

# Ensure venv is active
if (-not (Test-Path env:VIRTUAL_ENV)) {
    Write-Host "❌ Virtual environment not activated!" -ForegroundColor Red
    Write-Host "Please run:  venv\Scripts\activate"
    exit
}

# Get current site-packages path
$python = "python"
$sitePath = & $python -c "import site; print(site.getsitepackages()[0])"
Write-Host "`n📂 Using site-packages path: $sitePath"

# Step 1: Uninstall all possibly conflicting versions
Write-Host "`n🧹 Cleaning up old installations..." -ForegroundColor Yellow
pip uninstall -y moviepy imageio imageio-ffmpeg proglog | Out-Null

# Step 2: Reinstall cleanly
Write-Host "`n📦 Installing stable MoviePy (2.0.0)..." -ForegroundColor Green
pip install moviepy==2.0.0 --no-cache-dir

# Step 3: Verify folder presence
Write-Host "`n🔍 Checking installation directory..." -ForegroundColor Cyan
$moviepyDir = Join-Path $sitePath "moviepy"
if (Test-Path $moviepyDir) {
    Write-Host "✅ MoviePy package folder found at: $moviepyDir" -ForegroundColor Green
} else {
    Write-Host "⚠️ MoviePy folder missing. Reinstall may have failed." -ForegroundColor Yellow
}

# Step 4: Test import
Write-Host "`n🧠 Verifying MoviePy import..." -ForegroundColor Cyan
try {
    & $python -c "from moviepy.editor import VideoFileClip; print('✅ MoviePy is working correctly!')"
} catch {
    Write-Host "❌ Import test failed. MoviePy still not detected." -ForegroundColor Red
}

Write-Host "`n🎯 Done!" -ForegroundColor Cyan
