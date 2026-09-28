<template>
  <view :class="['page', { dark: isDark }]">
    <view v-if="favorites.length === 0" class="empty fade-up">
      <text class="empty-emoji">⭐</text>
      <text class="empty-title">还没有收藏</text>
      <text class="empty-text text-secondary">遇到好奇的问题，点亮星星收藏它</text>
      <button class="btn-solid empty-btn press" @click="goHome">去首页逛逛</button>
    </view>
    <view v-else class="list fade-up">
      <view
        v-for="(item, i) in favorites"
        :key="item.id"
        class="item"
        @click="goDetail(item)"
        @longpress="onRemove(item)"
      >
        <text class="no no-num">{{ i + 1 }}</text>
        <text class="q">{{ item.q }}</text>
        <view class="del press" @click.stop="onRemove(item)"><text class="del-x">✕</text></view>
      </view>
      <view class="tip text-secondary">长按或点 ✕ 取消收藏</view>
    </view>
  </view>
</template>

<script setup>
import { favorites, removeFav } from '@/common/store.js'
import { isDark } from '@/common/theme.js'

function onRemove(item) {
  uni.showModal({
    title: '取消收藏',
    content: item.q,
    confirmText: '删除',
    success: (res) => { if (res.confirm) removeFav(item.id) }
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
.empty {
  display: flex; flex-direction: column; align-items: center; gap: 16rpx;
  padding: 200rpx 64rpx 0;
}
.empty-emoji { font-size: 96rpx; }
.empty-title { font-size: 34rpx; font-weight: 600; }
.empty-text { font-size: 26rpx; color: var(--text); opacity: 0.68; }
.empty-btn { margin-top: 32rpx; padding: 0 64rpx; }

.list { background: var(--card); margin: 24rpx 32rpx; border-radius: var(--radius-lg); box-shadow: var(--shadow-card); overflow: hidden; }
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
.tip { text-align: center; padding: 28rpx; font-size: 22rpx; letter-spacing: 2rpx; }
</style>
