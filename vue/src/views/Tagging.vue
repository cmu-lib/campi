<template>
  <b-container>
    <p>Select a tag to work on from the dropdown. If you select a tag different from your already-checked-out tag, that tag will be checked back in and made available to other users</p>
    <TagSelectMenu v-model="selected_tag" />
    <PytorchModelMenu v-model="pytorch_model" />
    <b-button :disabled="waiting_for_selections" variant="primary">Select seed photo...</b-button>
  </b-container>
</template>

<script>
// import { HTTP } from "@/main";
import TagSelectMenu from "@/components/tagging/TagSelectMenu.vue";
import PytorchModelMenu from "@/components/PytorchModelMenu.vue";
export default {
  name: "Tagging",
  components: { TagSelectMenu, PytorchModelMenu },
  data() {
    return {
      selected_tag: null,
      pytorch_model: null
    };
  },
  computed: {
    waiting_for_selections() {
      return !(!!this.selected_tag & !!this.pytorch_model);
    }
  },
  methods: {
    submit() {
      // On input, register the tag task and then push the user to photo selection
      if (
        this.selected_tag.tasks.filter(
          task => task.pytorch_model.id == this.pytorch_model
        ).length == 1
      ) {
        // If a task has already been registered with this tag/model combo, PATCH it to assign the current user
      } else {
        // Otherwise, POST a new TaggingTask
      }
    }
  }
};
</script>