<script>
import { initTheme } from '@/common/theme.js'

export default {
  onLaunch: function () {
    initTheme()
  }
}
</script>

<style>
/* 全局主题变量：各页面根 view 加 .page，深色模式加 .dark */
.page {
  --bg: #f6f7f9;
  --card: #ffffff;
  --text: #1a1a1a;
  --text-secondary: #888888;
  --border: #e5e5e5;
  --accent: #4a80ff;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}
.page.dark {
  --bg: #16181d;
  --card: #22252c;
  --text: #e8e8e8;
  --text-secondary: #8a8f99;
  --border: #34383f;
  --accent: #6a9bff;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16rpx;
}
.text-secondary {
  color: var(--text-secondary);
}
.accent {
  color: var(--accent);
}
</style>
