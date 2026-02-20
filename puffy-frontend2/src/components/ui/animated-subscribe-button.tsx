"use client";

import { AnimatePresence, motion } from "framer-motion";

interface AnimatedSubscribeButtonProps {
  subscribeStatus: boolean;
  initialText: React.ReactElement | string;
  changeText: React.ReactElement | string;
  handleSubscribe: () => void;
  handleUnsubscribe: () => void;
  fontSize?: string;
  height?: string;
  width?: string;
}

export const AnimatedSubscribeButton: React.FC<
  AnimatedSubscribeButtonProps
> = ({
  subscribeStatus,
  changeText,
  initialText,
  handleSubscribe,
  handleUnsubscribe,
  fontSize,
  height,
  width,
}) => {
  return (
    <AnimatePresence mode="wait">
      {subscribeStatus ? (
        <motion.button
          className="relative flex items-center justify-center rounded-full bg-transparent border-[2px] border-black"
          onClick={handleUnsubscribe}
          initial={{ opacity: 0, scale: 1 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          exit={{ opacity: 0 }}
          // Only apply hover effect on non-touch devices
          variants={{
            hover: {
              scale: 1.05,
            },
          }}
          style={{
            height: height,
            width: width,
          }}
        >
          <motion.span
            key="action"
            className="relative flex h-full w-full items-center justify-center font-medium text-black"
            initial={{ y: -50 }}
            animate={{ y: 0 }}
            style={{
              fontSize: fontSize,
            }}
          >
            {changeText}
            <svg
              width="10"
              height="6"
              viewBox="0 0 10 6"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="ml-2"
            >
              <path
                d="M1 1L5 5L9 1"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </motion.span>
        </motion.button>
      ) : (
        <motion.button
          className="relative flex cursor-pointer items-center justify-center rounded-full bg-black text-white"
          onClick={handleSubscribe}
          initial={{ opacity: 0, scale: 1 }}
          animate={{ opacity: 1, scale: 1 }}
          whileTap={{ scale: 0.95 }}
          exit={{ opacity: 0 }}
          // Only apply hover effect on non-touch devices
          variants={{
            hover: {
              scale: 1.05,
            },
          }}
          whileHover={["hover", "@media (hover: hover) and (pointer: fine)"]}
          style={{
            height: height,
            width: width,
          }}
        >
          <motion.span
            key="reaction"
            className="relative flex items-center justify-center font-medium"
            initial={{ x: 0 }}
            exit={{ x: 50, transition: { duration: 0.1 } }}
            style={{
              fontSize: fontSize,
            }}
          >
            {initialText}
          </motion.span>
        </motion.button>
      )}
    </AnimatePresence>
  );
};
