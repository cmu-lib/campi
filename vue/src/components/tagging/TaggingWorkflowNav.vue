<template>
  <b-row class="my-3" align-h="center">
    <b-nav pills>
      <b-nav-item
        v-for="nav in nav_items"
        :key="nav.label"
        :active="nav.active"
        :disabled="nav.disabled"
        :to="nav.to"
      >{{ nav.label }}</b-nav-item>
    </b-nav>
  </b-row>
</template>

<script>
export default {
  name: "TaggingWorkflowNav",
  computed: {
    nav_items() {
      var tagging_nav = {
        label: "Select tag",
        to: { name: "Tagging" },
        disabled: true,
        active: false
      };
      var seed_nav = {
        label: "Choose seed photo",
        to: { name: "TaggingSeedPhotoBrowse", params: { tag: null } },
        disabled: true,
        active: false
      };
      var execution_nav = {
        label: "Begin tagging",
        to: {
          name: "TaggingExecution",
          params: { tag: null, seed_photo_id: null }
        },
        disabled: true,
        active: false
      };

      var rt = this.$route;
      if (rt.name == "Tagging") {
        tagging_nav.active = true;
        tagging_nav.disabled = false;
      } else if (rt.name == "TaggingSeedPhotoBrowse") {
        tagging_nav.disabled = false;
        seed_nav.active = true;
        seed_nav.disabled = false;
        seed_nav.to.params.tag = rt.params.tag;
      } else if (rt.name == "TaggingExecution") {
        tagging_nav.disabled = false;
        seed_nav.disabled = false;
        execution_nav.disabled = false;
        execution_nav.active = true;
        execution_nav.to.params.tag = rt.params.tag;
        execution_nav.to.params.seed_photo_id = rt.params.seed_photo_id;
      }

      return [tagging_nav, seed_nav, execution_nav];
    }
  }
};
</script>