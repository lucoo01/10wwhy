<template>
  <view :class="['page', { dark: isDark }]">
    <view class="list fade-up">
      <view
        v-for="(item, i) in visible"
        :key="item.id"
        class="row"
        @click="goDetail(item)"
      >
        <view class="row-no">
          <text class="no">NO.</text>
          <text class="no no-num">{{ i + 1 }}</text>
        </view>
        <text class="q">{{ item.q }}</text>
        <text v-if="isLiked(item.id)" class="like-flag">♥︎</text>
      </view>
    </view>
    <view v-if="loading" class="tip text-secondary">加载中…</view>
    <view v-else-if="visible.length >= total" class="end">
      <view class="end-line"></view>
      <text class="end-text text-secondary">已到尽头 · 共 {{ total }} 问</text>
      <view class="end-line"></view>
    </view>
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
  // 列表项经响应式代理后引用会变，按 id 定位下标
  const pos = item.pos !== undefined ? item.pos : all.findIndex((x) => x.id === item.id)
  if (pos < 0) return
  uni.navigateTo({ url: `/pages/detail/detail?groupId=${groupId}&pos=${pos}` })
}
</script>

<style scoped>
.list { background: var(--card); margin: 24rpx 32rpx; border-radius: var(--radius-lg); box-shadow: var(--shadow-card); overflow: hidden; }
.row {
  display: flex; align-items: center; gap: 20rpx;
  padding: 30rpx 32rpx;
  border-bottom: 1px solid var(--border);
}
.row:last-child { border-bottom: none; }
.row:active { background: var(--accent-soft); }
.row-no { display: flex; flex-direction: column; align-items: flex-start; min-width: 72rpx; }
.no-num { font-size: 30rpx; color: var(--text); opacity: 0.55; }
.q { flex: 1; font-size: 30rpx; line-height: 1.6; }
.like-flag { font-size: 28rpx; color: var(--accent); }

.tip { text-align: center; padding: 32rpx; font-size: 26rpx; }
.end { display: flex; align-items: center; gap: 24rpx; padding: 40rpx 64rpx calc(40rpx + env(safe-area-inset-bottom)); }
.end-line { flex: 1; height: 1px; background: var(--border); }
.end-text { font-size: 22rpx; letter-spacing: 2rpx; }
</style>
