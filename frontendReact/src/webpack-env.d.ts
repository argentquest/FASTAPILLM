/// <reference types="node" />

declare const process: {
  env: {
    NODE_ENV: 'development' | 'production' | 'test';
    API_URL?: string;
    APP_NAME?: string;
    APP_VERSION?: string;
  };
};

declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.txt' {
  const content: string;
  export default content;
}