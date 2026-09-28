<script>
import { initTheme } from '@/common/theme.js'

export default {
  onLaunch: function () {
    initTheme()
  }
}
</script>

<style>
/* ============ 设计系统：现代编辑部风 ============ */
/* 各页面根 view 加 .page，深色模式加 .dark */
.page {
  /* 色彩 */
  --bg: #f7f4ef;
  --card: #fffdf9;
  --card-flat: #f2eee6;
  --text: #1c1a17;
  --text-secondary: #8a8378;
  --border: #e8e2d8;
  --border-strong: #d8d0c2;
  --accent: #c8401f;
  --accent-soft: rgba(200, 64, 31, 0.08);
  --accent-border: rgba(200, 64, 31, 0.28);
  /* 字体 */
  --font-serif: Georgia, "Noto Serif SC", "Source Han Serif SC", "Songti SC", SimSun, serif;
  --font-sans: -apple-system, BlinkMacSystemFont, "PingFang SC", "HarmonyOS Sans SC", "MiSans", "Microsoft YaHei", sans-serif;
  /* 圆角 */
  --radius-lg: 24rpx;
  --radius-md: 16rpx;
  --radius-full: 999rpx;
  /* 阴影 */
  --shadow-card: 0 2rpx 12rpx rgba(28, 26, 23, 0.04);

  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  min-height: 100vh;
}
.page.dark {
  --bg: #131210;
  --card: #1d1b18;
  --card-flat: #232019;
  --text: #eae6de;
  --text-secondary: #948d81;
  --border: #2c2925;
  --border-strong: #3a3630;
  --accent: #e05a35;
  --accent-soft: rgba(224, 90, 53, 0.12);
  --accent-border: rgba(224, 90, 53, 0.4);
  --shadow-card: 0 2rpx 12rpx rgba(0, 0, 0, 0.25);
}

/* ============ 工具类 ============ */
.font-serif { font-family: var(--font-serif); }
.font-sans { font-family: var(--font-sans); }
.text-secondary { color: var(--text-secondary); }
.accent { color: var(--accent); }

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

/* 统一按压反馈 */
.press { transition: transform 0.12s ease, opacity 0.12s ease, background-color 0.12s ease; }
.press:active { transform: scale(0.97); opacity: 0.85; }

/* 内容进场动画 */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14rpx); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.32s ease both; }
.fade-up-1 { animation: fadeUp 0.32s ease 0.05s both; }
.fade-up-2 { animation: fadeUp 0.32s ease 0.1s both; }

/* 衬线序号（NO.1024） */
.no {
  font-family: var(--font-serif);
  font-size: 22rpx;
  letter-spacing: 2rpx;
  color: var(--text-secondary);
}

/* 胶囊描边按钮 */
.btn-outline {
  background: transparent;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-full);
  color: var(--text);
  font-size: 28rpx;
  line-height: 2.4;
}
/* 胶囊主按钮 */
.btn-solid {
  background: var(--accent);
  border-radius: var(--radius-full);
  color: #fff;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 2.4;
}
.page.dark .btn-solid { background: #d5502a; }
button::after { border: none; }
</style>
