import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from "@/views/Home.vue"
import Browse from '@/views/Browse.vue'
import Photo from "@/views/Photo.vue"
import Similarity from "@/views/Similarity.vue"
import CloseMatch from "@/views/CloseMatch.vue"
import CloseMatchRun from "@/views/CloseMatchRun.vue"
import CloseMatchRunDetail from "@/views/CloseMatchRunDetail.vue"
import CloseMatchRunList from "@/views/CloseMatchRunList.vue"
import Tags from "@/views/Tags.vue"
import Tagging from "@/views/Tagging.vue"
import TaggingTagSelect from "@/views/TaggingTagSelect.vue"
import TaggingSeedPhotoBrowse from "@/views/TaggingSeedPhotoBrowse.vue"
import TaggingExecution from "@/views/TaggingExecution.vue"
import Faces from "@/views/Faces.vue"
import Objects from "@/views/Objects.vue"
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: "/browse",
    name: "Browse",
    component: Browse,
  },
  {
    path: "/browse/photograph/:id",
    name: "Photo",
    component: Photo,
    props: (route) => {
      return { id: Number(route.params.id) }
    }
  },
  {
    path: "/similiarity/photograph/:id",
    name: "Similarity",
    component: Similarity,
    props: (route) => {
      return { seed_image_id: Number(route.params.id) }
    },
  },
  {
    path: "/close_match",
    name: "CloseMatch",
    component: CloseMatch,

  },
  {
    name: "CloseMatchRun",
    path: "/close_match/run/:id",
    component: CloseMatchRun,
    props: (route) => {
      return { close_match_run_id: Number(route.params.id) }
    },
    children: [
      {
        name: "CloseMatchRunList",
        path: "list",
        component: CloseMatchRunList,
        props: (route) => {
          return { close_match_run_id: Number(route.params.id) }
        }
      },
      {
        name: "CloseMatchRunDetail",
        path: ":set_id",
        component: CloseMatchRunDetail,
        props: (route) => {
          return { close_match_set_id: Number(route.params.set_id), close_match_run_id: Number(route.params.id) }
        }
      }
    ]
  },
  {
    name: "Tags",
    path: "/tags",
    component: Tags,
  },
  {
    path: "/tagging",
    component: Tagging,
    children: [
      {
        name: "TaggingTagSelect",
        path: "select",
        component: TaggingTagSelect
      },
      {
        name: "TaggingTask",
        path: ":task_id",
        props: (route) => {
          return { task_id: Number(route.params.task_id) }
        },
      },
      {
        name: "TaggingSeedPhotoBrowse",
        path: ":task_id/browse",
        component: TaggingSeedPhotoBrowse,
        props: (route) => {
          return { task_id: Number(route.params.task_id) }
        },
      },
      {
        name: "TaggingExecution",
        path: ":task_id/:seed_photo_id",
        component: TaggingExecution,
        props: (route) => {
          return {
            task_id: Number(route.params.task_id),
            seed_photo_id: Number(route.params.seed_photo_id)
          }
        }
      }
    ]
  },
  {
    name: "Faces",
    path: "/gcv/faces",
    component: Faces
  },
  {
    name: "Objects",
    path: "/gcv/objects",
    component: Objects
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
