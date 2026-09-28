// 数据层：加载 index.json 与分片 JSON，分片缓存用 markRaw 避免大数据进响应式
import { markRaw } from 'vue'

let indexPromise = null
// groupId -> { name, count, shards, shardData: [数组|null...], idIndex: Map|null }
const groupCache = {}

function readJson(path) {
  // #ifdef H5
  return new Promise((resolve, reject) => {
    uni.request({
      url: '/static/data/' + path,
      success: (res) => resolve(res.data),
      fail: reject
    })
  })
  // #endif
  // #ifdef APP-PLUS
  return new Promise((resolve, reject) => {
    plus.io.resolveLocalFileSystemURL('_www/static/data/' + path, (entry) => {
      entry.file((file) => {
        const reader = new plus.io.FileReader()
        reader.onloadend = (e) => {
          try { resolve(JSON.parse(e.target.result)) } catch (err) { reject(err) }
        }
        reader.onerror = reject
        reader.readAsText(file, 'utf-8')
      }, reject)
    }, reject)
  })
  // #endif
}

export function loadIndex() {
  if (!indexPromise) {
    indexPromise = readJson('index.json').then((idx) => {
      idx.groups.forEach((g) => {
        groupCache[g.id] = { ...g, shardData: g.shards.map(() => null) }
      })
      return idx
    })
  }
  return indexPromise
}

function loadShard(groupId, shardNo) {
  const g = groupCache[groupId]
  if (!g) return Promise.reject(new Error('unknown group ' + groupId))
  if (g.shardData[shardNo]) return Promise.resolve(g.shardData[shardNo])
  return readJson(g.shards[shardNo]).then((data) => {
    g.shardData[shardNo] = markRaw(data)
    return data
  })
}

// 返回某个分组已加载的全量数组（加载全部分片，切片缓存共享）
export async function loadGroup(groupId) {
  const g = groupCache[groupId] || (await loadIndex(), groupCache[groupId])
  const parts = []
  for (let i = 0; i < g.shards.length; i++) {
    parts.push(await loadShard(groupId, i))
  }
  return parts.flat()
}

// 取某分组内第 pos 条（0 基），自动加载所在分片
export async function getAt(groupId, pos) {
  const g = groupCache[groupId]
  const shardNo = Math.floor(pos / 5000)
  const shard = await loadShard(groupId, shardNo)
  return shard[pos - shardNo * 5000] || null
}

// 随机抽一条：随机分组 -> 随机位置
export async function getRandom() {
  const idx = await loadIndex()
  const g = idx.groups[Math.floor(Math.random() * idx.groups.length)]
  const pos = Math.floor(Math.random() * g.count)
  const item = await getAt(g.id, pos)
  return { ...item, groupId: g.id, groupName: g.name, pos }
}

// 分组内关键词搜索（调用前需 loadGroup）
export async function searchInGroup(groupId, keyword, limit = 200) {
  const all = await loadGroup(groupId)
  const out = []
  for (let i = 0; i < all.length && out.length < limit; i++) {
    if (all[i].q.includes(keyword)) out.push({ ...all[i], pos: i })
  }
  return out
}
