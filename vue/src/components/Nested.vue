<template>
  <span>
    <ol v-if="Array.isArray(value)">
      <li v-for="(item, index) in value" :key="index">
        <Nested :value="item" />
      </li>
    </ol>
    <ul v-else-if="typeof value == 'object' && !!value">
      <li v-for="(val, name) in value" :key="name">
        {{ name }}:
        <Nested :value="val" />
      </li>
    </ul>
    <span v-else>{{ value }}</span>
  </span>
</template>

<script>
export default {
  name: "Nested",
  props: ["value"]
};
</script>
