<template>
  <b-form-group
    id="tag-help"
    description="Which tag will you check out to work on?"
    label="Tag"
    label-for="tag-select"
    required
  >
    <b-form-select
      id="tag-select"
      v-if="!!tag_menu_options"
      :options="tag_menu_options"
      :value="value"
      @input="$emit('input', $event)"
    />
  </b-form-group>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "TagSelectMenu",
  props: {
    value: Number,
    default: null
  },
  computed: {
    tag_menu_options() {
      if (!!this.tags) {
        const current_tag = {
          label: "Your checked-out tags",
          options: this.tags
            .filter(
              tag =>
                tag.tasks.filter(
                  task => task.assigned_user.id == this.current_user.id
                ).length >= 1
            )
            .map(tag => {
              return { text: tag.label, value: tag };
            })
        };

        const open_tags = {
          label: "Available tags",
          options: this.tags
            .filter(tag => tag.tasks.every(task => task.assigned_user == null))
            .map(tag => {
              return { text: tag.label, value: tag };
            })
        };

        const taken_tags = {
          label: "Other users' tags",
          options: this.tags
            .filter(
              tag =>
                tag.tasks.every(
                  task => task.assigned_user != this.current_user.id
                ).length >= 1
            )
            .map(tag => {
              return { text: tag.label, value: tag, disabled: true };
            })
        };

        return [current_tag, open_tags, taken_tags];
      } else {
        return null;
      }
    },
    current_user() {
      return this.$root.user;
    }
  },
  asyncComputed: {
    tags() {
      return HTTP.get("tagging/tag/").then(
        results => {
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>