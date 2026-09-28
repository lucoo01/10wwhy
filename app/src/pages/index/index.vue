<template>
  <view :class="['page', { dark: isDark }]">
    <view class="topbar">
      <view class="search-box card" @click="goSearch">
        <text class="text-secondary">🔍 搜索问题</text>
      </view>
      <view class="actions">
        <button class="action-btn random" @click="randomOne">🎲 随机一题</button>
        <button class="action-btn history" @click="goHistory">🕘 历史</button>
      </view>
    </view>
    <view class="grid">
      <view
        v-for="g in groups"
        :key="g.id"
        class="group-card card"
        @click="goList(g)"
      >
        <text class="group-name">{{ g.name }}</text>
        <text class="group-count text-secondary">{{ g.count }} 条</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { loadIndex, getRandom } from '@/common/db.js'
import { isDark } from '@/common/theme.js'

const groups = ref([])

onShow(async () => {
  const idx = await loadIndex()
  groups.value = idx.groups
})

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
.topbar { padding: 24rpx; }
.search-box { padding: 20rpx 28rpx; font-size: 28rpx; }
.actions { display: flex; gap: 20rpx; margin-top: 20rpx; }
.action-btn {
  flex: 1; font-size: 30rpx; border-radius: 16rpx; border: none;
  padding: 10rpx 0; color: #fff;
}
.action-btn.random { background: var(--accent); }
.action-btn.history { background: var(--card); color: var(--text); border: 1px solid var(--border); }
.grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20rpx; padding: 0 24rpx 24rpx;
}
.group-card { padding: 32rpx 24rpx; display: flex; flex-direction: column; gap: 8rpx; }
.group-name { font-size: 32rpx; font-weight: 600; }
.group-count { font-size: 24rpx; }
</style>
