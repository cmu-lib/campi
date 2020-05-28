import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from "@/views/Home.vue"
import Browse from '@/views/Browse.vue'
import Photo from "@/views/Photo.vue"

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
    props: (route) => ({
      job: route.query.job,
      job_id: route.query.job,
      directory: route.query.directory
    })
  },
  {
    path: "/browse/photograph/:id",
    name: "Photo",
    component: Photo,
    props: true
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
