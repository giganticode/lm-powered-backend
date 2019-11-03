import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Page404 from '../views/Page404.vue'
import LanguagemodelDebugger from '../views/LanguagemodelDebugger.vue'
import LanguagemodelPrediction from '../views/LanguagemodelPrediction.vue'
import LanguagemodelSearch from '../views/LanguagemodelSearch.vue'
import LanguagemodelComparator from '../views/LanguagemodelComparator.vue'
import OverviewProjects from '../views/OverviewProjects.vue'
import OverviewProjectFiles from '../views/OverviewProjectFiles.vue'
import OverviewSingleFile from '../views/OverviewSingleFile.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/home',
    name: 'home',
    component: Home
  },
  {
    path: '/debugger',
    name: 'lmDebugger',
    component: LanguagemodelDebugger
  },
  {
    path: '/prediction',
    name: 'prediction',
    component: LanguagemodelPrediction
  },
  {
    path: '/search',
    name: 'search',
    component: LanguagemodelSearch
  },
  {
    path: '/comparator',
    name: 'lmComparator',
    component: LanguagemodelComparator
  },
  {
    path: '/overview',
    name: 'overview',
    component: OverviewProjects
  },
  {
    path: '/overview/:projecthash',
    name: 'overview',
    component: OverviewProjectFiles
  },
  {
    path: '/overview/:projecthash/:filehash',
    name: 'overview',
    component: OverviewSingleFile
  },
  {
    path: '/about',
    name: 'about',
    component: About,
  },
  {
    path: '*',
    name: 'page404',
    component: Page404
  },
]
const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router