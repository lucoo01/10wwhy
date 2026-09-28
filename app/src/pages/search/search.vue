<template>
  <view :class="['page', { dark: isDark }]">
    <view class="bar">
      <input
        class="input card"
        v-model="keyword"
        placeholder="输入关键词"
        confirm-type="search"
        @confirm="doSearch"
      />
      <picker mode="selector" :range="groupNames" :value="pickerIdx" @change="onGroupChange">
        <view class="picker card">{{ currentGroupName }} ▾</view>
      </picker>
    </view>
    <view v-if="searched && results.length === 0" class="tip text-secondary">无匹配结果</view>
    <view
      v-for="item in results"
      :key="item.id"
      class="item card"
      @click="goDetail(item)"
    >
      {{ item.q }}
    </view>
    <view v-if="results.length >= 200" class="tip text-secondary">仅显示前 200 条</view>
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

function goDetail(item) {
  uni.navigateTo({ url: `/pages/detail/detail?groupId=${groupId.value}&pos=${item.pos}` })
}
</script>

<style scoped>
.bar { display: flex; gap: 16rpx; padding: 24rpx; }
.input { flex: 1; padding: 16rpx 24rpx; font-size: 28rpx; color: var(--text); }
.picker { padding: 16rpx 24rpx; font-size: 28rpx; white-space: nowrap; }
.item { margin: 16rpx 24rpx 0; padding: 28rpx; font-size: 30rpx; line-height: 1.6; }
.tip { text-align: center; padding: 48rpx; font-size: 26rpx; }
</style>
