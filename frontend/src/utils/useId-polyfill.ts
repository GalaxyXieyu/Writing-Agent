// useId polyfill for Vue3 compatibility
import { getCurrentInstance } from 'vue'

let idCounter = 0

export function useId(): string {
	const instance = getCurrentInstance()
	if (instance) {
		const uid = instance.uid
		return `uni-id-${uid}-${++idCounter}`
	}
	return `uni-id-${++idCounter}`
}

