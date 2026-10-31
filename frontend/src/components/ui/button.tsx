import { Button as BaseButton } from '@base-ui/react/button'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import type { ComponentProps } from 'react'

const variants = cva('inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#09A8A3] disabled:opacity-55 disabled:cursor-not-allowed', {
  variants: {
    variant: {
      primary: 'bg-[#0C777C] text-white hover:bg-[#095F63] shadow-sm',
      accent: 'bg-[#F2AD59] text-[#142B3B] hover:bg-[#FFC17A]',
      outline: 'border border-[#D6E3EA] bg-white text-[#20445C] hover:bg-[#EDF4F8]',
      subtle: 'bg-transparent text-[#567082] hover:bg-[#EBF2F6]'
    },
    size: { sm: 'px-3 py-2 text-xs', md: 'px-4 py-2.5 text-sm', lg: 'px-5 py-3 text-sm' }
  },
  defaultVariants: {variant: 'primary', size: 'md'}
})

type Props = ComponentProps<typeof BaseButton> & VariantProps<typeof variants>
export function Button({className, variant, size, ...props}: Props) {
  return <BaseButton className={cn(variants({variant, size}), className)} {...props}/>
}
