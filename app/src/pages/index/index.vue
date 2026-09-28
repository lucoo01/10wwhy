<template>
  <view :class="['page', { dark: isDark }]">
    <!-- 品牌头部 -->
    <view class="hero fade-up">
      <view class="hero-row">
        <view class="seal"></view>
        <text class="hero-sub text-secondary">探索 · {{ totalCount.toLocaleString() }} 个问题</text>
      </view>
      <text class="hero-title font-serif">十万个为什么</text>
    </view>

    <!-- 搜索 + 操作 -->
    <view class="topbar fade-up-1">
      <view class="search-box press" @click="goSearch">
        <image class="search-icon" src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23948d81'%20stroke-width='2'%20stroke-linecap='round'%3E%3Ccircle%20cx='11'%20cy='11'%20r='7'/%3E%3Cline%20x1='16.5'%20y1='16.5'%20x2='21'%20y2='21'/%3E%3C/svg%3E" />
        <text class="search-ph text-secondary">搜索问题…</text>
      </view>
      <view class="actions">
        <button class="btn-solid action-btn press" @click="randomOne">随机一问</button>
        <button class="btn-outline action-btn press" @click="goHistory">浏览历史</button>
      </view>
    </view>

    <!-- 分类目录 -->
    <view class="catalog fade-up-2">
      <view class="catalog-head">
        <text class="catalog-title">分类目录</text>
        <text class="no">CATALOGUE</text>
      </view>
      <view
        v-for="(g, i) in groups"
        :key="g.id"
        class="catalog-item press"
        @click="goList(g)"
      >
        <text class="cat-no no">{{ String(i + 1).padStart(2, '0') }}</text>
        <text class="cat-emoji">{{ emojiOf(g.id) }}</text>
        <text class="cat-name">{{ g.name }}</text>
        <text class="cat-count text-secondary">{{ formatCount(g.count) }}</text>
        <text class="cat-arrow text-secondary">›</text>
      </view>
    </view>
    <view class="footer text-secondary">左右滑动切换 · 收藏你好奇的问题</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { loadIndex, getRandom } from '@/common/db.js'
import { isDark } from '@/common/theme.js'

// 分类 emoji 图标（按分组 id）
const EMOJI = {
  1: '🩺', 2: '🧠', 3: '🌿', 4: '🧪', 5: '👥', 6: '⚛️',
  7: '💪', 8: '⚙️', 9: '🪐', 10: '🌍', 11: '🍵', 12: '📜',
  13: '💡', 14: '🔢', 15: '📈'
}

const groups = ref([])
const totalCount = ref(0)

onShow(async () => {
  const idx = await loadIndex()
  groups.value = idx.groups
  totalCount.value = idx.groups.reduce((s, g) => s + g.count, 0)
})

function emojiOf(id) { return EMOJI[id] || '📘' }
function formatCount(n) {
  return n >= 10000 ? (n / 10000).toFixed(1).replace(/\.0$/, '') + ' 万' : String(n)
}

function goList(g) {
  uni.navigateTo({ url: `/pages/list/list?groupId=${g.id}&name=${encodeURIComponent(g.name)}` })
}
function goSearch() {
  uni.navigateTo({ url: '/pages/search/search' })
}
function goHistory() {
  uni.navigateTo({ url: '/pages/history/history' })
}
async function randomOne() {
  uni.showLoading({ title: '抽取中' })
  try {
    const item = await getRandom()
    uni.hideLoading()
    uni.navigateTo({
      url: `/pages/detail/detail?groupId=${item.groupId}&pos=${item.pos}`
    })
  } catch (e) {
    uni.hideLoading()
  }
}
</script>

<style scoped>
.hero { padding: 48rpx 40rpx 8rpx; }
.hero-row { display: flex; align-items: center; gap: 16rpx; }
/* 朱砂红小色块：印章感 */
.seal { width: 20rpx; height: 20rpx; background: var(--accent); border-radius: 4rpx; }
.hero-sub { font-size: 24rpx; letter-spacing: 4rpx; }
.hero-title {
  display: block;
  font-size: 64rpx;
  font-weight: 700;
  letter-spacing: 6rpx;
  margin-top: 12rpx;
}

.topbar { padding: 32rpx 32rpx 0; }
.search-box {
  display: flex; align-items: center; gap: 16rpx;
  background: var(--card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-full);
  padding: 22rpx 32rpx;
}
.search-icon { width: 32rpx; height: 32rpx; }
.search-ph { font-size: 28rpx; }
.actions { display: flex; gap: 20rpx; margin-top: 24rpx; }
.action-btn { flex: 1; padding: 0; }

.catalog { margin: 40rpx 32rpx 0; background: var(--card); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); overflow: hidden; }
.catalog-head {
  display: flex; align-items: baseline; justify-content: space-between;
  padding: 32rpx 32rpx 20rpx; border-bottom: 1px solid var(--border);
}
.catalog-title { font-size: 30rpx; font-weight: 600; letter-spacing: 2rpx; }
.catalog-item {
  display: flex; align-items: center; gap: 20rpx;
  padding: 28rpx 32rpx;
  border-bottom: 1px solid var(--border);
}
.catalog-item:last-child { border-bottom: none; }
.catalog-item:active { background: var(--accent-soft); }
.cat-emoji { font-size: 36rpx; }
.cat-name { flex: 1; font-size: 30rpx; font-weight: 500; }
.cat-count { font-size: 24rpx; font-variant-numeric: tabular-nums; color: var(--text); opacity: 0.7; }
.cat-arrow { font-size: 36rpx; line-height: 1; opacity: 0.6; }

.footer {
  text-align: center; font-size: 22rpx; letter-spacing: 2rpx;
  padding: 40rpx 0 calc(32rpx + env(safe-area-inset-bottom));
}
</style>
