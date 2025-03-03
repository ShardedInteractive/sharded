// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Sharded',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://docs.sharded.app',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',


  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',


  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            'https://github.com/shardedinteractive/docs/edit/main/sharded/docs/',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: true,
        respectPrefersColorScheme: false,
      },

      navbar: {
        logo: {
          alt: 'Sharded',
          src: 'img/sharded_transparent.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'doc',
            position: 'left',
            label: 'Docs',
          },
          {
            type: 'docSidebar',
            sidebarId: 'enterprise',
            position: 'right',
            label: 'Enterprise',
          },
          // {
          //   type: 'docsVersionDropdown',
          //   position: 'right',
          //   dropdownItemsAfter: [{to: '/versions', label: 'All versions'}],
          //   dropdownActiveClassDisabled: true,
          // },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Introduction',
                to: '/',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Discord',
                href: 'https://discord.gg/4BK9vjpg87',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/shardedinteractive',
              },
              {
                label: 'Privacy Policy',
                href: 'https://sharded.app/privacy',
              },
              {
                label: 'Terms of Service',
                href: 'https://sharded.app/terms',
              }
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Sharded Interactive, Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
