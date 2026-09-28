<template>
  <view :class="['page', { dark: isDark }]">
    <view class="bar fade-up">
      <input
        class="input press"
        v-model="keyword"
        placeholder="输入关键词…"
        confirm-type="search"
        @confirm="doSearch"
      />
      <picker mode="selector" :range="groupNames" :value="pickerIdx" @change="onGroupChange">
        <view class="picker press">{{ currentGroupName }} ▾</view>
      </picker>
    </view>
    <view class="result fade-up-1">
      <view v-if="searched && results.length === 0" class="empty">
        <text class="empty-emoji">🔍</text>
        <text class="empty-text text-secondary">没有找到「{{ keyword }}」相关问题</text>
      </view>
      <view
        v-for="(item, i) in results"
        :key="item.id"
        class="item"
        @click="goDetail(item)"
      >
        <text class="no no-num">{{ i + 1 }}</text>
        <view class="q-wrap">
          <text v-for="(seg, j) in highlight(item.q)" :key="j" :class="['q-seg', { hit: seg.hit }]">{{ seg.text }}</text>
        </view>
      </view>
      <view v-if="results.length >= 200" class="tip text-secondary">仅显示前 200 条</view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { loadIndex, searchInGroup } from '@/common/db.js'
import { isDark } from '@/common/theme.js'

const keyword = ref('')
const groups = ref([])
const groupId = ref(0)
const results = ref([])
const searched = ref(false)
let timer = null

const groupNames = computed(() => groups.value.map((g) => g.name))
const pickerIdx = computed(() => groups.value.findIndex((g) => g.id === groupId.value))
const currentGroupName = computed(() => groups.value[pickerIdx.value]?.name || '选择分类')

onLoad(async () => {
  const idx = await loadIndex()
  groups.value = idx.groups
  groupId.value = idx.groups[0].id
})

function onGroupChange(e) {
  groupId.value = groups.value[Number(e.detail.value)].id
  if (keyword.value.trim()) doSearch()
}

// 输入防抖 300ms 自动搜索
watch(keyword, () => {
  clearTimeout(timer)
  if (!keyword.value.trim()) { results.value = []; searched.value = false; return }
  timer = setTimeout(doSearch, 300)
})

async function doSearch() {
  const kw = keyword.value.trim()
  if (!kw) return
  results.value = await searchInGroup(groupId.value, kw)
  searched.value = true
}

// 把问题拆成 命中/未命中 片段，命中段渲染为 accent 色
function highlight(q) {
  const kw = keyword.value.trim()
  const idx = kw ? q.indexOf(kw) : -1
  if (idx < 0) return [{ text: q, hit: false }]
  return [
    { text: q.slice(0, idx), hit: false },
    { text: kw, hit: true },
    { text: q.slice(idx + kw.length), hit: false }
  ].filter((s) => s.text)
}

function goDetail(item) {
  uni.navigateTo({ url: `/pages/detail/detail?groupId=${groupId.value}&pos=${item.pos}` })
}
</script>

<style scoped>
.bar { display: flex; gap: 16rpx; padding: 24rpx 32rpx; }
.input {
  flex: 1; padding: 20rpx 32rpx; font-size: 28rpx; color: var(--text);
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-full);
}
.input:focus { border-color: var(--accent); }
.picker {
  padding: 20rpx 28rpx; font-size: 26rpx; white-space: nowrap;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-full); color: var(--text);
}

.result { background: var(--card); margin: 16rpx 32rpx; border-radius: var(--radius-lg); box-shadow: var(--shadow-card); overflow: hidden; }
.item {
  display: flex; align-items: baseline; gap: 20rpx;
  padding: 28rpx 32rpx;
  border-bottom: 1px solid var(--border);
}
.item:last-child { border-bottom: none; }
.item:active { background: var(--accent-soft); }
.no-num { min-width: 48rpx; }
.q-wrap { flex: 1; font-size: 30rpx; line-height: 1.6; }
.q-seg { color: var(--text); }
.q-seg.hit { color: var(--accent); font-weight: 600; }

.empty { display: flex; flex-direction: column; align-items: center; gap: 16rpx; padding: 96rpx 0; }
.empty-emoji { font-size: 64rpx; }
.empty-text { font-size: 26rpx; }
.tip { text-align: center; padding: 32rpx; font-size: 24rpx; background: var(--card); margin: 0 32rpx; border-radius: var(--radius-lg); }
</style>
