import { createRootRoute, Outlet } from '@tanstack/react-router'
import {AppSidebar} from "@/components/app-sidebar.tsx";
import {SidebarProvider} from "@/components/ui/sidebar.tsx";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";

const queryClient = new QueryClient()

export const Route = createRootRoute({
    component: () => (
        <div className="w-screen h-screen">
            <QueryClientProvider client={queryClient}>
            <SidebarProvider>
                <AppSidebar />
                <hr />
                <Outlet />
                {/* <TanStackRouterDevtools /> */}
            </SidebarProvider>
            </QueryClientProvider>
        </div>
    ),
})