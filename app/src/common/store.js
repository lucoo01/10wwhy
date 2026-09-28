// 收藏 / 点赞 / 浏览历史：uni.Storage 持久化，模块级响应式状态
import { ref } from 'vue'

const FAV_KEY = 'fav_v1'     // [{id, q, groupId}]
const LIKE_KEY = 'like_v1'   // [id]
const HISTORY_KEY = 'hist_v1' // [{id, q, groupId, pos}] 最新在前，上限 500
const HISTORY_MAX = 500

function read(key, def) {
  try { return uni.getStorageSync(key) || def } catch (e) { return def }
}
function write(key, val) {
  try { uni.setStorageSync(key, val) } catch (e) {}
}

export const favorites = ref(read(FAV_KEY, []))
export const likes = ref(new Set(read(LIKE_KEY, [])))
export const history = ref(read(HISTORY_KEY, []))

export function isFav(id) {
  return favorites.value.some((f) => f.id === id)
}
export function toggleFav(item) {
  if (isFav(item.id)) {
    favorites.value = favorites.value.filter((f) => f.id !== item.id)
  } else {
    favorites.value = [{ id: item.id, q: item.q, groupId: item.groupId, pos: item.pos }, ...favorites.value]
  }
  write(FAV_KEY, favorites.value)
}
export function removeFav(id) {
  favorites.value = favorites.value.filter((f) => f.id !== id)
  write(FAV_KEY, favorites.value)
}

export function isLiked(id) {
  return likes.value.has(id)
}
export function toggleLike(id) {
  const s = new Set(likes.value)
  s.has(id) ? s.delete(id) : s.add(id)
  likes.value = s
  write(LIKE_KEY, [...s])
}

export function addHistory(item) {
  let h = history.value.filter((x) => x.id !== item.id)
  h.unshift({ id: item.id, q: item.q, groupId: item.groupId, pos: item.pos })
  if (h.length > HISTORY_MAX) h = h.slice(0, HISTORY_MAX)
  history.value = h
  write(HISTORY_KEY, h)
}
export function removeHistory(id) {
  history.value = history.value.filter((x) => x.id !== id)
  write(HISTORY_KEY, history.value)
}
export function clearHistory() {
  history.value = []
  write(HISTORY_KEY, [])
}
