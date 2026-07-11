<template>
  <div
    ref="trackRef"
    class="drag-verify"
    :class="{ 'is-passed': modelValue, 'is-resetting': isResetting }"
  >
    <div class="drag-verify__progress" :style="progressStyle" />
    <div class="drag-verify__text">{{ modelValue ? '验证成功' : '按住滑块拖动' }}</div>
    <div
      class="drag-verify__handler"
      :style="{ left: `${offset}px` }"
      @mousedown.prevent="onMouseDown"
      @touchstart.prevent="onTouchStart"
    >
      <el-icon v-if="modelValue"><ele-Select /></el-icon>
      <el-icon v-else><ele-DArrowRight /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts" name="DragVerify">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';

const HANDLER_SIZE = 40;
const RESET_DURATION = 500;

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits<{ (e: 'update:modelValue', value: boolean): void }>();

const trackRef = ref<HTMLDivElement>();
const offset = ref(0);
const isResetting = ref(false);
const dragging = ref(false);
const startX = ref(0);
const startOffset = ref(0);
let resetTimer: number | null = null;

const getMax = () => {
  if (!trackRef.value) return 0;
  return Math.max(0, trackRef.value.offsetWidth - HANDLER_SIZE);
};

const progressStyle = computed(() => {
  if (props.modelValue) return { width: '100%' };
  return { width: `${offset.value + HANDLER_SIZE / 2}px` };
});

const updateOffset = (value: number) => {
  offset.value = value;
};

const finishDrag = () => {
  if (!dragging.value) return;
  dragging.value = false;
  const max = getMax();
  if (offset.value >= max - 2) {
    updateOffset(max);
    emit('update:modelValue', true);
    return;
  }
  isResetting.value = true;
  emit('update:modelValue', false);
  if (resetTimer) window.clearTimeout(resetTimer);
  resetTimer = window.setTimeout(() => {
    updateOffset(0);
    isResetting.value = false;
    resetTimer = null;
  }, RESET_DURATION);
};

const onMove = (clientX: number) => {
  if (!dragging.value || props.modelValue) return;
  const delta = clientX - startX.value;
  const max = getMax();
  updateOffset(Math.min(Math.max(startOffset.value + delta, 0), max));
};

const onMouseDown = (event: MouseEvent) => {
  if (props.modelValue) return;
  dragging.value = true;
  startX.value = event.clientX;
  startOffset.value = offset.value;
};

const onTouchStart = (event: TouchEvent) => {
  if (props.modelValue) return;
  dragging.value = true;
  startX.value = event.touches[0].clientX;
  startOffset.value = offset.value;
};

const onMouseMove = (event: MouseEvent) => onMove(event.clientX);
const onTouchMove = (event: TouchEvent) => {
  if (!dragging.value) return;
  event.preventDefault();
  onMove(event.touches[0].clientX);
};

watch(
  () => props.modelValue,
  (value) => {
    if (!value) {
      updateOffset(0);
      isResetting.value = false;
    }
  }
);

onMounted(() => {
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', finishDrag);
  document.addEventListener('touchmove', onTouchMove, { passive: false });
  document.addEventListener('touchend', finishDrag);
});

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', onMouseMove);
  document.removeEventListener('mouseup', finishDrag);
  document.removeEventListener('touchmove', onTouchMove);
  document.removeEventListener('touchend', finishDrag);
  if (resetTimer) window.clearTimeout(resetTimer);
});
</script>

<style scoped lang="scss">
.drag-verify {
  --drag-verify-text: #6b7280;
  position: relative;
  width: 100%;
  height: 40px;
  overflow: hidden;
  border: 1px solid #dbdfe9;
  border-radius: 8px;
  background: #f1f1f4;
  user-select: none;
}

.drag-verify__progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 8px 0 0 8px;
  background: var(--el-color-primary);
  transition: none;
}

.drag-verify.is-passed .drag-verify__progress {
  width: 100% !important;
  background: #57d187;
}

.drag-verify.is-resetting .drag-verify__progress {
  width: 0 !important;
  transition: width 0.5s ease;
}

.drag-verify__text {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: var(--drag-verify-text);
  pointer-events: none;
}

.drag-verify.is-passed .drag-verify__text {
  color: #fff;
}

.drag-verify__handler {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 2;
  display: flex;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 1px 4px rgb(0 0 0 / 12%);
  color: #6b7280;
  cursor: grab;
  touch-action: none;
}

.drag-verify.is-resetting .drag-verify__handler {
  transition: left 0.5s ease;
}

.drag-verify.is-passed .drag-verify__handler {
  color: #57d187;
}
</style>
