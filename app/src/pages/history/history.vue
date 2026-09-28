<template>
  <view :class="['page', { dark: isDark }]">
    <view v-if="history.length" class="toolbar fade-up">
      <text class="count text-secondary">共 {{ history.length }} 条足迹</text>
      <button class="clear-btn press" @click="onClear">清空</button>
    </view>
    <view v-if="history.length === 0" class="empty fade-up">
      <text class="empty-emoji">🕘</text>
      <text class="empty-title">暂无浏览历史</text>
      <text class="empty-text text-secondary">看过的每一个为什么，都会留在这里</text>
      <button class="btn-solid empty-btn press" @click="goHome">去首页逛逛</button>
    </view>
    <view v-else class="list fade-up">
      <view
        v-for="(item, i) in history"
        :key="item.id"
        class="item"
        @click="goDetail(item)"
        @longpress="onRemove(item)"
      >
        <text class="no no-num">{{ i + 1 }}</text>
        <text class="q">{{ item.q }}</text>
        <view class="del press" @click.stop="onRemove(item)"><text class="del-x">✕</text></view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { history, removeHistory, clearHistory } from '@/common/store.js'
import { isDark } from '@/common/theme.js'

function onRemove(item) { removeHistory(item.id) }
function onClear() {
  uni.showModal({
    title: '清空历史',
    content: '确定清空全部浏览历史？',
    success: (res) => { if (res.confirm) clearHistory() }
  })
}
function goDetail(item) {
  uni.navigateTo({ url: `/pages/detail/detail?groupId=${item.groupId}&pos=${item.pos || 0}` })
}
function goHome() {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style scoped>
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 24rpx 32rpx;
}
.count { font-size: 24rpx; letter-spacing: 2rpx; }
.clear-btn {
  background: transparent; border: 1px solid var(--accent-border);
  border-radius: var(--radius-full); color: var(--accent);
  font-size: 24rpx; line-height: 2; padding: 0 40rpx; margin: 0;
}

.empty {
  display: flex; flex-direction: column; align-items: center; gap: 16rpx;
  padding: 180rpx 64rpx 0;
}
.empty-emoji { font-size: 96rpx; }
.empty-title { font-size: 34rpx; font-weight: 600; }
.empty-text { font-size: 26rpx; color: var(--text); opacity: 0.68; }
.empty-btn { margin-top: 32rpx; padding: 0 64rpx; }

.list { background: var(--card); margin: 8rpx 32rpx 32rpx; border-radius: var(--radius-lg); box-shadow: var(--shadow-card); overflow: hidden; }
.item {
  display: flex; align-items: center; gap: 20rpx;
  padding: 28rpx 32rpx;
  border-bottom: 1px solid var(--border);
}
.item:active { background: var(--accent-soft); }
.no-num { min-width: 48rpx; }
.q { flex: 1; font-size: 30rpx; line-height: 1.6; }
.del {
  width: 56rpx; height: 56rpx; border-radius: 50%;
  background: var(--card-flat);
  display: flex; align-items: center; justify-content: center;
}
.del:active { background: var(--accent-soft); }
.del:active .del-x { color: var(--accent); }
.del-x { color: var(--text-secondary); font-size: 26rpx; }
</style>
