<template>
  <view
    :class="['page', { dark: isDark }]"
    @touchstart="onTouchStart"
    @touchend="onTouchEnd"
  >
    <view v-if="item" class="content">
      <view class="meta text-secondary">{{ groupName }} · 第 {{ pos + 1 }} / {{ total }} 条</view>
      <view class="q card">{{ item.q }}</view>
      <view class="actions">
        <button class="btn" @click="onFav">{{ fav ? '★ 已收藏' : '☆ 收藏' }}</button>
        <button class="btn" @click="onLike">{{ liked ? '❤️ 已赞' : '🤍 点赞' }}</button>
      </view>
      <view class="nav">
        <button class="btn nav-btn" :disabled="pos <= 0" @click="go(pos - 1)">← 上一题</button>
        <button class="btn nav-btn" :disabled="pos >= total - 1" @click="go(pos + 1)">下一题 →</button>
      </view>
      <view class="tip text-secondary">左右滑动切换问题</view>
    </view>
    <view v-else class="tip text-secondary">加载中…</view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { loadIndex, getAt } from '@/common/db.js'
import { isFav, toggleFav, isLiked, toggleLike, addHistory, favorites, likes } from '@/common/store.js'
import { isDark } from '@/common/theme.js'

const item = ref(null)
const pos = ref(0)
const total = ref(0)
const groupName = ref('')
let groupId = 0

const fav = computed(() => item.value && (favorites.value, isFav(item.value.id)))
const liked = computed(() => item.value && (likes.value, isLiked(item.value.id)))

onLoad(async (query) => {
  groupId = Number(query.groupId)
  pos.value = Number(query.pos || 0)
  const idx = await loadIndex()
  const g = idx.groups.find((x) => x.id === groupId)
  groupName.value = g.name
  total.value = g.count
  await show(pos.value)
})

async function show(p) {
  const it = await getAt(groupId, p)
  if (!it) return
  pos.value = p
  item.value = { ...it, groupId, pos: p }
  addHistory(item.value)
}

function go(p) {
  if (p >= 0 && p < total.value) show(p)
}
function onFav() { toggleFav(item.value) }
function onLike() { toggleLike(item.value.id) }

// 左右滑动切换
let startX = 0
function onTouchStart(e) { startX = e.changedTouches[0].clientX }
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - startX
  if (dx < -60) go(pos.value + 1)
  else if (dx > 60) go(pos.value - 1)
}
</script>

<style scoped>
.content { padding: 32rpx 24rpx; display: flex; flex-direction: column; gap: 32rpx; }
.meta { font-size: 26rpx; }
.q { padding: 48rpx 36rpx; font-size: 40rpx; line-height: 1.7; font-weight: 600; }
.actions, .nav { display: flex; gap: 20rpx; }
.btn {
  flex: 1; font-size: 30rpx; border-radius: 16rpx; background: var(--card);
  color: var(--text); border: 1px solid var(--border); padding: 8rpx 0;
}
.btn[disabled] { opacity: 0.4; }
.tip { text-align: center; font-size: 24rpx; padding: 24rpx; }
</style>
