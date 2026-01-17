<template>
  <canvas
    ref="canvasRef"
    :width="width"
    :height="height"
    @click="refreshCode"
    class="captcha-canvas"
  ></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';

interface Props {
  width?: number;
  height?: number;
  length?: number;
}

const props = withDefaults(defineProps<Props>(), {
  width: 120,
  height: 40,
  length: 4
});

const emit = defineEmits<{
  (e: 'update:code', code: string): void;
}>();

const canvasRef = ref<HTMLCanvasElement>();
const code = ref('');

// 生成随机颜色
const randomColor = (min: number, max: number): string => {
  const r = randomNum(min, max);
  const g = randomNum(min, max);
  const b = randomNum(min, max);
  return `rgb(${r},${g},${b})`;
};

// 生成随机数
const randomNum = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min) + min);
};

// 生成验证码字符
const generateCode = (): string => {
  const chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';
  let code = '';
  for (let i = 0; i < props.length; i++) {
    code += chars[randomNum(0, chars.length)];
  }
  return code;
};

// 绘制验证码
const drawCode = () => {
  if (!canvasRef.value) return;
  
  const ctx = canvasRef.value.getContext('2d');
  if (!ctx) return;

  // 生成新的验证码
  code.value = generateCode();
  emit('update:code', code.value);

  // 清空画布
  ctx.clearRect(0, 0, props.width, props.height);

  // 绘制背景
  ctx.fillStyle = randomColor(180, 240);
  ctx.fillRect(0, 0, props.width, props.height);

  // 绘制验证码文字
  for (let i = 0; i < code.value.length; i++) {
    const char = code.value[i];
    const fontSize = randomNum(20, 28);
    ctx.font = `${fontSize}px Arial`;
    ctx.fillStyle = randomColor(50, 160);
    
    // 随机旋转角度
    const angle = randomNum(-30, 30) * Math.PI / 180;
    const x = (props.width / (props.length + 1)) * (i + 1);
    const y = props.height / 2 + fontSize / 3;
    
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.fillText(char, 0, 0);
    ctx.restore();
  }

  // 绘制干扰线
  for (let i = 0; i < 5; i++) {
    ctx.strokeStyle = randomColor(100, 200);
    ctx.lineWidth = randomNum(1, 2);
    ctx.beginPath();
    ctx.moveTo(randomNum(0, props.width), randomNum(0, props.height));
    ctx.lineTo(randomNum(0, props.width), randomNum(0, props.height));
    ctx.stroke();
  }

  // 绘制干扰点
  for (let i = 0; i < 30; i++) {
    ctx.fillStyle = randomColor(0, 255);
    ctx.beginPath();
    ctx.arc(
      randomNum(0, props.width),
      randomNum(0, props.height),
      1,
      0,
      2 * Math.PI
    );
    ctx.fill();
  }
};

// 刷新验证码
const refreshCode = () => {
  drawCode();
};

// 获取验证码值
const getCode = (): string => {
  return code.value;
};

onMounted(() => {
  drawCode();
});

// 监听尺寸变化
watch(() => [props.width, props.height, props.length], () => {
  drawCode();
});

defineExpose({
  refreshCode,
  getCode
});
</script>

<style scoped lang="scss">
.captcha-canvas {
  cursor: pointer;
  border-radius: 4px;
  vertical-align: middle;
  
  &:hover {
    opacity: 0.8;
  }
}
</style>
