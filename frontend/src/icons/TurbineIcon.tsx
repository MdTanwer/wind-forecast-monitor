import type { SVGProps } from "react";

export function TurbineIcon({
  width = 22,
  height = 22,
  className,
  ...props
}: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 32 32"
      width={width}
      height={height}
      className={className}
      fill="currentColor"
      {...props}
    >
      <circle cx="16" cy="16" r="2.2" />
      <path d="M16 13.2c.4-3.6 2.2-6.4 4.6-7.6-.6 3.2-.2 5.6 1.2 7.2-2.2.2-4 .6-5.8.4Z" />
      <path d="M18.6 17.4c3.4 1.2 6.6.6 8.4-1.2-2.6 1.8-5.2 2-7.6 1.2-.4 2.2-1.4 3.8-2.8 5 1-2 .8-3.8 0-5Z" />
      <path d="M13.6 16.8c-2.8-2.2-3.4-5.2-2.4-8 1.2 2.8 1.4 5.2.4 7.2-1.4 1.6-2.2 3.6-2.2 5.6 2.2-1.2 3.6-2.8 4.2-4.8Z" />
      <path d="M15.2 18.2v9.2h1.6v-9.2" />
    </svg>
  );
}
