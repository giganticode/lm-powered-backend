<template>
  <div id="app">
    <div uk-sticky="sel-target: .uk-navbar-container; cls-active: uk-navbar-sticky; bottom: #transparent-sticky-navbar">
      <nav class="uk-navbar-container" uk-navbar style="position: relative; z-index: 980;">
        <div class="uk-container">
          <div class="uk-navbar-left">
            <ul class="uk-navbar-nav">
              <li>
                <router-link to="/home">Home</router-link>
              </li>
              <li>
                <router-link to="/debugger">LM-Debugger</router-link>
              </li>
              <li>
                <router-link to="/comparator">LM-Comparator</router-link>
              </li>
              <li>
                <router-link to="/prediction">Prediction</router-link>
              </li>
              <li>
                <router-link to="/search">Search</router-link>
              </li>
              <li>
                <router-link to="/overview">Project-Overview</router-link>
              </li>
              <li>
                <router-link to="/about">About</router-link>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </div>

    <div class="uk-container uk-padding">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: "App"
};
</script>

<style lang="less">
@import "../node_modules/uikit/src/less/uikit.less";

.router-link-active {
  border-bottom: solid 3px #333;
}

/* Navbar */
.uk-navbar-item,
.uk-navbar-nav > li > a,
.uk-navbar-toggle {
  min-height: 50px;
}
.uk-navbar-container .uk-container {
  width: 100%;
}
.uk-navbar-nav > li.uk-active > a {
  border-bottom: solid;
}

.colors .uk-input {
  width: 73px;
  height: 30px;
}

/* Loading */
.loading svg circle {
    stroke-width: 2px !important;
    color: #0422cc;
}
.loading .uk-modal-dialog {
	width: unset;
	border-radius: 20px
}

/* Line-number */
pre {
  padding: 0 10px;
  margin: 5px 0;
  white-space: nowrap;
  border: 1px solid #e5e5e5;
  border-radius: 5px;
  min-height: 50px;

  &.line-numbers {
    span.line:before{
      text-align: right;
      content: counter(line);
      display: inline-block;
      border-right: 1px solid #ddd;
      padding-right: 5px;
      margin-right: 0.5em;
      color: rgb(131, 131, 131);
      width: 30px;
      box-sizing: border-box;
    }
  }

  span.line {
    display: block;
    line-height: 1.5;
    counter-increment: line;
  }

  span.token {
    display: initial;
    margin-right: 1px;
  }

  span.token:not(.whitespace):empty::before {
    content: '\00b6';
  }

  span.token.whitespace {
    white-space: pre;
  }

  span.line:empty:after {
    content: " ";
    white-space: pre;
  }

  &.token-framing {
    span.token:not(.whitespace) {
        border: solid 1px #333;
        box-sizing: border-box;
    }
  }

  &:not(.use-colors) {
    span.token {
      color: #111 !important;
    }
  }

  &:not(.visualize-entropies) {
    span {
      background-color: transparent !important;
    }
  }

}

.split {
  height: unset;
}

.gutter.gutter-horizontal {
  width: 10px;
  background-color: transparent !important;
}

.uk-table-small {
  th, td {
    padding: 2px 12px;
  }
}

.uk-card-default {
    background: #fff;
    color: #666;
    box-shadow: 0 5px 15px rgba(0,0,0,.08);
}

.uk-input, .uk-select, .uk-textarea {
    background: #fff;
    color: #666;
    border: 1px solid #e5e5e5;
    transition-property: color,background-color,border;
}

.uk-input:focus, .uk-select:focus, .uk-textarea:focus {
    outline: 0;
    background-color: #fff;
    color: #666;
    border-color: #1e87f0;
}

textarea {
  font-family: Consolas, monaco, monospace !important;
  resize: vertical;
}

.uk-button.uk-button-text.uk-icon {
  line-height: 1;
}

.uk-no-link, .uk-no-link:hover, .uk-no-link:active {
  text-decoration: none;
  color: initial;
}

.uk-pointer {
  cursor: pointer;
}

.noselect, label {
  -webkit-touch-callout: none; /* iOS Safari */
    -webkit-user-select: none; /* Safari */
     -khtml-user-select: none; /* Konqueror HTML */
       -moz-user-select: none; /* Old versions of Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
            user-select: none; /* Non-prefixed version, currently supported by Chrome, Opera and Firefox */
}

// Tooltip
.tooltip {
  display: block !important;
  z-index: 10000;

  .tooltip-inner {
    background: black;
    color: white;
    border-radius: 16px;
    padding: 5px 10px 4px;
  }

  .tooltip-arrow {
    width: 0;
    height: 0;
    border-style: solid;
    position: absolute;
    margin: 5px;
    border-color: black;
    z-index: 1;
  }

  &[x-placement^="top"] {
    margin-bottom: 5px;

    .tooltip-arrow {
      border-width: 5px 5px 0 5px;
      border-left-color: transparent !important;
      border-right-color: transparent !important;
      border-bottom-color: transparent !important;
      bottom: -5px;
      left: calc(50% - 5px);
      margin-top: 0;
      margin-bottom: 0;
    }
  }

  &[x-placement^="bottom"] {
    margin-top: 5px;

    .tooltip-arrow {
      border-width: 0 5px 5px 5px;
      border-left-color: transparent !important;
      border-right-color: transparent !important;
      border-top-color: transparent !important;
      top: -5px;
      left: calc(50% - 5px);
      margin-top: 0;
      margin-bottom: 0;
    }
  }

  &[x-placement^="right"] {
    margin-left: 5px;

    .tooltip-arrow {
      border-width: 5px 5px 5px 0;
      border-left-color: transparent !important;
      border-top-color: transparent !important;
      border-bottom-color: transparent !important;
      left: -5px;
      top: calc(50% - 5px);
      margin-left: 0;
      margin-right: 0;
    }
  }

  &[x-placement^="left"] {
    margin-right: 5px;

    .tooltip-arrow {
      border-width: 5px 0 5px 5px;
      border-top-color: transparent !important;
      border-right-color: transparent !important;
      border-bottom-color: transparent !important;
      right: -5px;
      top: calc(50% - 5px);
      margin-left: 0;
      margin-right: 0;
    }
  }

  &[aria-hidden="true"] {
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.15s, visibility 0.15s;
  }

  &[aria-hidden="false"] {
    visibility: visible;
    opacity: 1;
    transition: opacity 0.15s;
  }
}

</style>