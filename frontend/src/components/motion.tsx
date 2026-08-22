import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

export function FadeIn({
  children,
  delay = 0,
  y = 14,
  className,
}: {
  children: ReactNode
  delay?: number
  y?: number
  className?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay, ease: [0.21, 0.47, 0.32, 0.98] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export const staggerContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
}

export const staggerItem = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: [0.21, 0.47, 0.32, 0.98] as const },
  },
}

export function Stagger({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className={className}
    >
      {children}
    </motion.div>
  )
}

export function StaggerItem({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <motion.div variants={staggerItem} className={className}>
      {children}
    </motion.div>
  )
}

/** Animated value reveal */
export function CountUp({
  value,
  suffix = '',
  decimals = 0,
}: {
  value: number | string
  suffix?: string
  decimals?: number
}) {
  const display = typeof value === 'number' ? value.toFixed(decimals) : value
  return (
    <motion.span
      key={display}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="inline-block tabular-nums"
    >
      {display}
      {suffix}
    </motion.span>
  )
}
