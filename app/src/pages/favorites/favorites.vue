<template>
  <view :class="['page', { dark: isDark }]">
    <view v-if="favorites.length === 0" class="tip text-secondary">还没有收藏，去首页逛逛吧</view>
    <view
      v-for="item in favorites"
      :key="item.id"
      class="item card"
      @click="goDetail(item)"
      @longpress="onRemove(item)"
    >
      <text class="q">{{ item.q }}</text>
      <text class="del" @click.stop="onRemove(item)">✕</text>
    </view>
    <view v-if="favorites.length" class="tip text-secondary">长按或点 ✕ 删除</view>
  </view>
</template>

<script setup>
import { favorites, removeFav } from '@/common/store.js'
import { isDark } from '@/common/theme.js'

function onRemove(item) {
  uni.showModal({
    title: '删除收藏',
    content: item.q,
    confirmText: '删除',
    success: (res) => { if (res.confirm) removeFav(item.id) }
  })
}
function goDetail(item) {
  uni.navigateTo({ url: `/pages/detail/detail?groupId=${item.groupId}&pos=${item.pos || 0}` })
}
</script>

<style scoped>
.item {
  margin: 16rpx 24rpx 0; padding: 28rpx; font-size: 30rpx; line-height: 1.6;
  display: flex; align-items: center; gap: 16rpx;
}
.q { flex: 1; }
.del { color: var(--text-secondary); padding: 0 12rpx; font-size: 32rpx; }
.tip { text-align: center; padding: 48rpx; font-size: 26rpx; }
</style>
