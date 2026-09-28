<template>
  <view :class="['page', { dark: isDark }]">
    <view
      v-for="item in visible"
      :key="item.id"
      class="item card"
      @click="goDetail(item)"
    >
      <text class="q">{{ item.q }}</text>
      <text v-if="isLiked(item.id)" class="like-flag">❤️</text>
    </view>
    <view v-if="loading" class="tip text-secondary">加载中…</view>
    <view v-else-if="visible.length >= total" class="tip text-secondary">— 到底了 —</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onReachBottom } from '@dcloudio/uni-app'
import { loadIndex, loadGroup } from '@/common/db.js'
import { isLiked } from '@/common/store.js'
import { isDark } from '@/common/theme.js'

const PAGE = 50
const visible = ref([])
const total = ref(0)
const loading = ref(false)
let all = []
let groupId = 0

onLoad(async (query) => {
  groupId = Number(query.groupId)
  uni.setNavigationBarTitle({ title: query.name || '问题列表' })
  loading.value = true
  await loadIndex()
  all = await loadGroup(groupId)
  total.value = all.length
  visible.value = all.slice(0, PAGE)
  loading.value = false
})

onReachBottom(() => {
  if (visible.value.length < all.length) {
    visible.value = all.slice(0, visible.value.length + PAGE)
  }
})

function goDetail(item) {
  uni.navigateTo({ url: `/pages/detail/detail?groupId=${groupId}&pos=${item.pos !== undefined ? item.pos : all.indexOf(item)}` })
}
</script>

<style scoped>
.item {
  margin: 16rpx 24rpx 0; padding: 28rpx; font-size: 30rpx; line-height: 1.6;
  display: flex; justify-content: space-between; align-items: center; gap: 16rpx;
}
.q { flex: 1; }
.tip { text-align: center; padding: 32rpx; font-size: 26rpx; }
</style>
