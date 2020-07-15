<template>
  <b-row class="my-3" align-h="center" align-v="center">
    <b-col cols="4"></b-col>
    <b-col cols="4">
      <b-nav pills v-if="!!nav_items">
        <b-nav-item
          v-for="nav in nav_items"
          :key="nav.label"
          :active="nav.active"
          :disabled="nav.disabled"
          :to="nav.to"
        >{{ nav.label }}</b-nav-item>
      </b-nav>
    </b-col>
    <b-col cols="4">
      <b-row align-h="around">
        <div v-if="!!task">
          Tag:
          <b-badge
            title="Click to check this tag back in and return to the tag selection screen."
            v-b-tooltip:hover
            @click="check_in_tag"
            class="pointer"
          >
            {{ task.tag.label }}
            <BIconXCircleFill class="ml-1" />
          </b-badge>
        </div>
        <div v-if="!!seed_photo">
          Seed photo:
          <b-badge id="seed_photo_popover">{{ seed_photo.filename }}</b-badge>
          <b-popover
            v-if="!!seed_photo"
            target="seed_photo_popover"
            triggers="hover"
            placement="left"
          >
            <template v-slot:title>{{ seed_photo.filename }}</template>
            <b-img :src="seed_photo.image.thumbnail" width="230" />
          </b-popover>
        </div>
      </b-row>
    </b-col>
  </b-row>
</template>

<script>
import { HTTP } from "@/main";
import { BIconXCircleFill } from "bootstrap-vue";
export default {
  name: "TaggingWorkflowNav",
  components: { BIconXCircleFill },
  computed: {
    task_id() {
      return this.$route.params.task_id;
    },
    seed_photo_id() {
      return this.$route.params.seed_photo_id;
    },
    nav_items() {
      const rt = this.$route;

      var tagging_nav = {
        label: "1. Select tag",
        to: { name: "TaggingTagSelect" },
        disabled: true,
        active: false
      };
      var seed_nav = {
        label: "2. Choose seed photo",
        to: { name: "TaggingSeedPhotoBrowse", params: { task_id: null } },
        disabled: true,
        active: false
      };
      var execution_nav = {
        label: "3. Begin tagging",
        to: {
          name: "TaggingExecution",
          params: { task_id: null, seed_photo_id: null }
        },
        disabled: true,
        active: false
      };

      if (rt.name == "TaggingTagSelect") {
        tagging_nav.active = true;
        tagging_nav.disabled = false;
      } else if (rt.name == "TaggingSeedPhotoBrowse") {
        tagging_nav.disabled = false;
        seed_nav.active = true;
        seed_nav.disabled = false;
        seed_nav.to.params.task_id = this.task_id;
      } else if (rt.name == "TaggingExecution") {
        tagging_nav.disabled = false;
        seed_nav.disabled = false;
        seed_nav.to.params.task_id = this.task_id;
        execution_nav.disabled = false;
        execution_nav.active = true;
        execution_nav.to.params.task_id = this.task_id;
        execution_nav.to.params.seed_photo_id = this.seed_photo_id;
      }

      return [tagging_nav, seed_nav, execution_nav];
    }
  },
  asyncComputed: {
    task() {
      if (!!this.task_id) {
        return HTTP.get(`/tagging/task/${this.task_id}/`).then(
          response => {
            return response.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    },
    seed_photo() {
      if (!!this.seed_photo_id) {
        return HTTP.get(`/photograph/${this.seed_photo_id}/`).then(
          response => {
            return response.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    }
  },
  methods: {
    check_in_tag() {
      HTTP.post(`tagging/task/${this.task_id}/check_in/`).then(
        response => {
          console.log(response);
          this.$router.push({ name: "TaggingTagSelect" });
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>