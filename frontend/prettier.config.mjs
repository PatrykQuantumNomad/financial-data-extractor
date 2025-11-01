/** @type {import('prettier').Config & import('prettier-plugin-tailwindcss').PluginOptions} */
const config = {
  plugins: [    
    "prettier-plugin-organize-imports",
    "prettier-plugin-packagejson",
    "prettier-plugin-tailwindcss",
  ],
  importOrder: [
    "<TYPES>",
    "<BUILTIN_MODULES>",
    "<THIRD_PARTY_MODULES>",
    "",
    "^@/(.*)$", // <-- matches tsconfig path alias
    "^[./]", // relative imports
  ],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
};

export default config;
