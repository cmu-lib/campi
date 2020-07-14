<template>
  <b-container>
    <p>Select a tag to work on from the dropdown. If you select a tag different from your already-checked-out tag, that tag will be checked back in and made available to other users</p>
    <TagSelectMenu v-model="selected_tag" @current_tag="set_current_tag" :key="tag_select_force" />
    <PytorchModelMenu v-model="pytorch_model" />
    <b-button-toolbar>
      <b-button
        :disabled="waiting_for_selections"
        variant="primary"
        @click="submit"
        class="mr-1"
      >Select seed photo...</b-button>
      <b-button
        v-if="!!current_tag"
        variant="danger"
        @click="check_in_current_tag"
        class="mr-1"
      >Check back in "{{ current_tag.text }}" tag</b-button>
    </b-button-toolbar>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import TagSelectMenu from "@/components/tagging/TagSelectMenu.vue";
import PytorchModelMenu from "@/components/PytorchModelMenu.vue";
export default {
  name: "TaggingTagSelect",
  components: { TagSelectMenu, PytorchModelMenu },
  data() {
    return {
      selected_tag: null,
      pytorch_model: null,
      current_tag: null,
      tag_select_force: 0
    };
  },
  computed: {
    waiting_for_selections() {
      return !(!!this.selected_tag & !!this.pytorch_model);
    }
  },
  methods: {
    set_current_tag(current_tag) {
      this.current_tag = current_tag;
    },
    check_in_current_tag() {
      const task_id = this.current_tag.value.id;
      HTTP.post(`tagging/task/${task_id}/check_in/`).then(
        response => {
          this.$bvToast.toast(response.data.success, { variant: "success" });
          this.current_tag = null;
          this.tag_select_force += 1;
        },
        error => {
          this.$bvToast.toast(error.data.error, { variant: "danger" });
        }
      );
    },
    submit() {
      // On input, register the tag task and then push the user to photo selection
      const existing_tasks = this.selected_tag.tasks.filter(
        task => task.pytorch_model.id == this.pytorch_model
      );
      if (existing_tasks.length == 1) {
        // If a task has already been registered with this tag/model combo, PATCH it to assign the current user
        HTTP.put(`tagging/task/${existing_tasks[0].id}/`, {
          tag: this.selected_tag.id,
          pytorch_model: this.pytorch_model
        }).then(
          response => {
            this.$router.push({
              name: "TaggingSeedPhotoBrowse",
              params: { task_id: response.data.id }
            });
          },
          error => {
            console.log(error);
          }
        );
      } else {
        // Otherwise, POST a new TaggingTask
        HTTP.post("tagging/task/", {
          tag: this.selected_tag.id,
          pytorch_model: this.pytorch_model,
          assigned_user: this.$root.user.id
        }).then(
          response => {
            this.$router.push({
              name: "TaggingSeedPhotoBrowse",
              params: { task_id: response.data.id }
            });
          },
          error => {
            console.log(error);
          }
        );
      }
    }
  }
};
</script>