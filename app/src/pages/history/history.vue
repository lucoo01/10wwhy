<template>
  <view :class="['page', { dark: isDark }]">
    <view v-if="history.length" class="toolbar">
      <text class="text-secondary">共 {{ history.length }} 条</text>
      <text class="clear" @click="onClear">清空</text>
    </view>
    <view v-if="history.length === 0" class="tip text-secondary">暂无浏览历史</view>
    <view
      v-for="item in history"
      :key="item.id"
      class="item card"
      @click="goDetail(item)"
      @longpress="onRemove(item)"
    >
      <text class="q">{{ item.q }}</text>
      <text class="del" @click.stop="onRemove(item)">✕</text>
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
</script>

<style scoped>
.toolbar {
  display: flex; justify-content: space-between; padding: 24rpx; font-size: 26rpx;
}
.clear { color: var(--accent); }
.item {
  margin: 16rpx 24rpx 0; padding: 28rpx; font-size: 30rpx; line-height: 1.6;
  display: flex; align-items: center; gap: 16rpx;
}
.q { flex: 1; }
.del { color: var(--text-secondary); padding: 0 12rpx; font-size: 32rpx; }
.tip { text-align: center; padding: 48rpx; font-size: 26rpx; }
</style>
