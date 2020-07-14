<template>
  <b-media>
    <template v-slot:aside>
      <b-img-lazy :src="photograph.image.thumbnail" width="400" />
    </template>
    <b-link
      :to="{name: 'Similarity', params: {id: photograph.id}, scrollBehavior: { x: 0, y: 0 }}"
      title="Click to set this image as the 'seed image'"
      v-b-tooltip:hover
    >
      <h6>{{ photograph.filename }}</h6>
    </b-link>
    <b-progress
      v-if="photograph.distance"
      :value="1-photograph.distance"
      max="1"
      variant="secondary"
      v-b-popover.hover.top="'Similarity is measured based on the cosine distance of this photograph\'s vector from the vector of the seed image.'"
      :title="'Distance: ' + photograph.distance"
    />
    <p>{{ photograph.date_taken_early }} - {{ photograph.date_taken_late }}</p>
    <b-row class="m-1">
      <b-badge
        variant="info"
        v-if="!!photograph.job"
        class="mx-1"
        :to="{name: 'Browse', query: {job: photograph.job.id}}"
      >
        <BIconCamera />
        {{ photograph.job.label }}
      </b-badge>
      <b-badge
        variant="primary"
        class="mx-1"
        :to="{name: 'Browse', query: {job: photograph.directory.id}}"
      >
        <BIconFolderFill />
        {{ photograph.directory.label }}
      </b-badge>
    </b-row>
    <b-row class="m-1">
      <b-badge
        v-for="pt in photograph.photograph_tags"
        :key="pt.id"
        variant="warning"
        class="mx-1"
        :to="{name: 'Browse', query: {tag: pt.tag.id}}"
      >
        <BIconTag />
        {{ pt.tag.label }}
      </b-badge>
    </b-row>
    <b-row class="m-1">
      <b-button
        variant="info"
        size="sm"
        :to="{name: 'Photo', params: {id: photograph.id}}"
      >Go to detail</b-button>
    </b-row>
  </b-media>
</template>

<script>
import { BIconCamera, BIconFolderFill, BIconTag } from "bootstrap-vue";
export default {
  name: "PhotographListItem",
  components: { BIconCamera, BIconFolderFill, BIconTag },
  props: {
    photograph: {
      type: Object,
      required: true
    }
  },
  methods: {
    get_variant(distance) {
      if (distance <= 0.39) {
        return "success";
      } else if ((distance > 0.39) & (distance <= 0.55)) {
        return "warning";
      } else {
        return "secondary";
      }
    }
  }
};
</script>