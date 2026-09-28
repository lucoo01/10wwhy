// 深色模式：跟随系统，向 document/body 根节点切换 theme 类
import { ref } from 'vue'

export const isDark = ref(false)

export function initTheme() {
  // #ifdef H5
  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  const apply = () => {
    isDark.value = mq.matches
    document.documentElement.classList.toggle('dark', mq.matches)
  }
  apply()
  mq.addEventListener('change', apply)
  // #endif
  // #ifdef APP-PLUS
  // App 端用 uni 系统信息判断，监听 onThemeChange?（App 端 page 样式由 CSS 变量 + 类控制）
  try {
    const info = uni.getSystemInfoSync()
    isDark.value = info.theme === 'dark' || info.osTheme === 'dark'
  } catch (e) {}
  uni.onThemeChange && uni.onThemeChange((res) => { isDark.value = res.theme === 'dark' })
  // #endif
}
