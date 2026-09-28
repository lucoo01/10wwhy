<template>
  <view
    :class="['page', { dark: isDark }]"
    @touchstart="onTouchStart"
    @touchend="onTouchEnd"
  >
    <view v-if="item" class="content fade-up" :key="item.id">
      <view class="chip">
        <text class="chip-text">{{ groupName }} · {{ pos + 1 }} / {{ total }}</text>
      </view>
      <view class="quote-wrap">
        <text class="quote-mark font-serif">“</text>
        <text class="q font-serif">{{ item.q }}</text>
      </view>
      <view class="actions">
        <view :class="['icon-btn', 'press', { on: fav }]" @click="onFav">
          <text class="icon">{{ fav ? '★︎' : '☆︎' }}</text>
          <text class="icon-label">{{ fav ? '已收藏' : '收藏' }}</text>
        </view>
        <view :class="['icon-btn', 'press', { on: liked }]" @click="onLike">
          <text class="icon icon-heart">{{ liked ? '♥︎' : '♡︎' }}</text>
          <text class="icon-label">{{ liked ? '已赞' : '点赞' }}</text>
        </view>
      </view>
      <view class="nav">
        <button class="btn-outline nav-btn press" :disabled="pos <= 0" @click="go(pos - 1)">← 上一题</button>
        <button class="btn-outline nav-btn press" :disabled="pos >= total - 1" @click="go(pos + 1)">下一题 →</button>
      </view>
      <view class="tip text-secondary">← 左右滑动切换问题 →</view>
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
.content {
  padding: 48rpx 40rpx calc(40rpx + env(safe-area-inset-bottom));
  display: flex; flex-direction: column; align-items: center; gap: 48rpx;
}
.chip {
  background: var(--accent-soft);
  border: 1px solid var(--accent-border);
  border-radius: var(--radius-full);
  padding: 8rpx 28rpx;
}
.chip-text { color: var(--accent); font-size: 24rpx; letter-spacing: 2rpx; }

.quote-wrap { position: relative; width: 100%; padding-top: 48rpx; }
.quote-mark {
  position: absolute; top: -28rpx; left: -8rpx;
  font-size: 120rpx; line-height: 1;
  color: var(--accent); opacity: 0.18;
}
.q {
  display: block;
  font-size: 48rpx;
  font-weight: 600;
  line-height: 1.8;
  text-align: center;
  letter-spacing: 2rpx;
}

.actions { display: flex; gap: 64rpx; }
.icon-btn {
  display: flex; flex-direction: column; align-items: center; gap: 8rpx;
  width: 128rpx; height: 128rpx;
  border-radius: 50%;
  background: var(--card);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-card);
  justify-content: center;
}
.icon-btn.on { background: var(--accent-soft); border-color: var(--accent-border); }
.icon { font-size: 44rpx; line-height: 1; }
.icon-heart { font-size: 40rpx; }
.icon-btn.on .icon { color: var(--accent); }
.icon-label { font-size: 22rpx; color: var(--text-secondary); }
.icon-btn.on .icon-label { color: var(--accent); }

.nav { display: flex; gap: 20rpx; width: 100%; }
.nav-btn { flex: 1; padding: 0; }
.nav-btn[disabled] { opacity: 0.45; }
.page.dark .quote-mark { opacity: 0.28; }

.tip { font-size: 22rpx; letter-spacing: 2rpx; }
</style>
