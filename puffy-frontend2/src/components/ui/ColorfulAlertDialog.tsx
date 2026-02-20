"use client";

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { fluidSize } from "@/lib/utils";

export default function Modal({
  children,
  isOpen,
}: {
  children?: React.ReactNode;
  isOpen: boolean;
}) {
  return (
    <AlertDialog open={isOpen}>
      <AlertDialogContent
        className="bg-white overflow-hidden"
        style={{
          borderRadius: fluidSize(20, 50),
          width: "90%",
          maxWidth: 800,
        }}
      >
        <AlertDialogTitle className="sr-only">Modal Dialog</AlertDialogTitle>
        {/* <div
          className="absolute"
          style={{
            background: "#770ED2",
            filter: "blur(200px)",
            pointerEvents: "none", // Prevent div from blocking interactions
            zIndex: -2, // Place behind content
            width: 615,
            height: 550,
            left: width < 700 ? -337 : -137,
            top: width < 700 ? -520 : -449,
          }}
          aria-hidden="true" // Hide from screen readers since it's decorative
        />
        <div
          className="absolute"
          style={{
            background: "#D86DF0",
            filter: "blur(200px)",
            pointerEvents: "none", // Prevent div from blocking interactions
            zIndex: -1, // Place behind content
            width: 441,
            height: 300,
            left: width < 700 ? 265 : 375,
            top: width < 700 ? -300 : -250,
          }}
          aria-hidden="true" // Hide from screen readers since it's decorative
        /> */}
        {children}
      </AlertDialogContent>
    </AlertDialog>
  );
}
